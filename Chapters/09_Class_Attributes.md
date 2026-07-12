# Class Attributes

Class-level attributes behave in ways that surprise programmers coming from C++ or Java.

## Class Attributes Are Not Default Values

A field declared in the class body, outside any method, is a *class attribute*.
It is easy to misread one as a per-object default value.
It is not.

> A class attribute creates a single shared variable across all instances of the class.

If you then create an instance variable of the same name,
that instance variable *shadows* the class attribute.
In C++ or Java, the language allocates storage for such a field in each object before the constructor runs,
which makes this behavior a surprise.

Here's an example showing why it can be confusing:

```python
# class_attribute_confusion.py

class Stars:
    rating = 5  # Shared across all instances

a, b = Stars(), Stars()
print(a.rating, b.rating)  # Both read the same storage
#: 5 5
a.rating = 1  # Assigning makes an instance variable on 'a'
print(a.rating, b.rating)  # 'a' shadows it, 'b' sees the class
#: 1 5
Stars.rating = 9  # Change the shared storage
print(a.rating, b.rating)  # 'b' reads the class attribute
#: 1 9
```

An instance and its class each have their own attribute dictionary.
Reading an attribute checks the instance first, then falls back to the class.
Assigning always writes to the instance,
creating the instance variable on first assignment.
To show this we can inspect the class with `vars(A)` and the instance with `vars(a)`:

```python
# inside_objects.py
class A:
    x = 100  # Class attribute

a = A()
print(vars(A)["x"])  # The attribute lives in the class dict
#: 100
print(vars(a))  # The instance has no attributes yet
#: {}
a.x = 1
print(vars(a))  # Assignment created it on the instance
#: {'x': 1}
print(vars(A)["x"])
#: 100
```

A class attribute seems like a default until someone assigns to an instance variable of the same name.
Changing the class attribute makes the "default" value seem different for every object that has not shadowed it.
This produces bugs that surface far from their cause.

When you genuinely want one shared value, say so with `ClassVar` from `typing`.
The checker then treats it as class-wide,
and stops you from accidentally creating an instance variable that shadows it:

```python
# class_var.py
from typing import ClassVar
from display import display_object

class Tally:
    total: ClassVar[int] = 0  # A single shared value
    label: str  # Declared, not yet assigned

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

display_object(Tally)
#: [Attributes]
#:   • total: typing.ClassVar[int] = 0 [CV]
#: [Methods]
#:   None
a = Tally("a")
display_object(a)
#: [Attributes]
#:   • label: str = 'a'
#:   • total: typing.ClassVar[int] = 1 [CV]
#: [Methods]
#:   None
b = Tally("b")
print(Tally.total)
#: 2
# a.total = 99  # ty: cannot assign ClassVar "total" via instance
```

`display_object(Tally)` shows what the class actually holds: `total`,
and nothing called `label`.
An assignment in the class body is what creates a class attribute,
as `class_attribute_confusion.py` showed above.
`total: ClassVar[int] = 0` has the `= 0`,
so it exists on `Tally` before any instance is built.
`label: str` has no `=`,
so nothing is stored under that name anywhere on the class.
The annotation only records, in `Tally.__annotations__`,
that a `Tally` will eventually carry a `label`.
That promise is invisible to `display_object()`,
which reports attributes that exist,
not annotations that merely describe one to come.

`display_object(a)` tells a different story once an instance exists.
Both `label` and `total` appear:
`label: str = 'a'` and `total: typing.ClassVar[int] = 1`.
Constructing `a` ran `self.label = label`,
which created a real `label` attribute on `a`, not on `Tally`.
`total` shows up too, not because `a` has its own copy,
but because reading an attribute checks the instance first,
then falls back to the class,
the same rule `Stars` demonstrated earlier in this chapter.

A *bare annotation*, one with no assigned value,
is a promise rather than a placeholder.
It states that instances of this class will carry a `label` attribute of type `str`,
set somewhere.
Here that somewhere is `__init__()`,
whose `self.label = label` is what `display_object(a)` above actually found.
Had `__init__()` never assigned it, no attribute would exist,
on the instance or the class.
The checker would not catch the omission,
because it trusts the annotation instead of verifying that every method actually sets it.
The failure would surface later,
as an `AttributeError` from the first code that reads the missing `label`.

The annotation on `label` is not required here.
Delete it, and `ty` still infers `label: str` correctly from `self.label = label`,
because the parameter's own type carries through to the attribute it initializes.
It earns its place for symmetry with `total`,
so the class's two attributes read together at the top instead of one hiding inside the constructor.
[Simulation](38_Simulation.md#a-robot-in-a-maze) shows the case where the annotation is not optional.
There, an attribute is set from outside the class entirely,
and a bare annotation is the checker's only way to know its type.

`ClassVar` is a hint for the checker, not the runtime.
It records that `total` belongs to the class,
and it catches the accidental shadowing from the earlier example before it happens.

## ClassVar and Inheritance

Subclasses inherit a `ClassVar` declared on a base class like any other class attribute.
A subclass that doesn't declare its own copy reads straight through to the base's value,
via the normal method resolution order.
A subclass that assigns its own value creates a separate class attribute,
independent of the base and of sibling subclasses:

```python
# class_var_inheritance.py
from typing import ClassVar

class Base:
    shared: ClassVar[int] = 0

class Left(Base):
    pass

class Right(Base):
    shared = 100  # Its own class attr, separate from Base's

print(Left.shared, Right.shared)
#: 0 100
Base.shared = 9  # Only affects subclasses that haven't overridden
print(Left.shared, Right.shared)
#: 9 100
Left.shared = 5  # Creates Left's own attribute, doesn't touch Base
print(Base.shared, Left.shared, Right.shared)
#: 9 5 100
```

`Left` has no `shared` of its own,
so it tracks `Base.shared` until something assigns to `Left.shared` directly.
`Right` overrode `shared` at class-definition time,
so it never sees changes made through `Base`.
`ClassVar` doesn't change any of this.
It only tells the checker that `shared` belongs to the class,
not that subclasses share storage.

For real per-object defaults, write a constructor with default arguments,
or use a `@dataclass`,
which turns the class-attribute syntax into instance variable defaults.
Each object then gets its own storage for instance variables:

```python
# real_defaults.py
from dataclasses import dataclass

class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # An instance variable, one per object

@dataclass
class B:
    x: int = 100  # Constructor default, not class attribute

a = A()
a.x = -1
print(a.x, A().x)  # The change in a does not leak
#: -1 100
print(B().x, B(7).x)
#: 100 7
```

A `@dataclass` reads the class-attribute declarations as a template and generates a constructor from them.
[Data Classes as Types](12_Data_Classes_as_Types.md#data-classes) covers the details.

## Exercises

1.  In `class_attribute_confusion.py`,
    add a third instance `c = Stars()` after the `Stars.rating = 9` line,
    and print `c.rating`.
    Predict its value before running,
    then explain why it differs from `a.rating`.
2.  In `class_var_inheritance.py`,
    add a third subclass `class Middle(Base): pass` (no override, like `Left`) and print `Middle.shared` alongside the others at each step.
    Confirm `Middle` tracks `Base` exactly like `Left` does.
3.  In `real_defaults.py`, create `b = B()` and assign `b.x = -1`.
    Then create a second instance, `b2 = B()`,
    and confirm `b2.x` is still `100`, unaffected.
4.  Rewrite `Tally` from `class_var.py` so `total` is a plain (non-`ClassVar`) class attribute instead,
    then have an instance assign to `self.total` directly and explain,
    using `vars()` as in `inside_objects.py`,
    what that assignment actually creates.
