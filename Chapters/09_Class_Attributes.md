# Class Attributes

Class-level attributes behave in ways that surprise programmers coming from C++ or Java.

## Class Attributes Are Not Default Values

A field declared in the class body, outside any method, is a *class attribute*.
It is easy to misread one as a per-object default value.
It is not.

> A class attribute creates a single shared variable across all instances of the class.

If you then create an instance attribute of the same name,
that instance attribute *shadows* the class attribute.
In C++ or Java, the language allocates storage for such a field in each object before the constructor runs,
which makes this behavior a surprise.
A Python class attribute is the equivalent of a C++ or Java `static` field.
Python has no syntax for declaring a per-object field in the class body;
per-object storage comes from assigning through `self` inside a method.

This example shows why it can be confusing:

```python
# class_attribute_confusion.py

class Stars:
    rating = 5  # Shared across all instances

a, b = Stars(), Stars()
print(a.rating, b.rating)  # Both read the same storage
#: 5 5
a.rating = 1  # Assigning makes an instance attribute on 'a'
print(a.rating, b.rating)  # 'a' shadows it, 'b' sees the class
#: 1 5
Stars.rating = 9  # Change the shared storage
print(a.rating, b.rating)  # 'b' reads the class attribute
#: 1 9
```

An instance and its class each have their own attribute dictionary.
Reading an attribute checks the instance first, then falls back to the class.
Assigning through an instance always writes to the instance,
creating the instance attribute on first assignment.
Assigning through the class name, as `Stars.rating = 9` did,
changes the shared value.
`vars(obj)` returns that dictionary,
so inspecting the class with `vars(A)` and the instance with `vars(a)` shows the split:

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

The listing subscripts `vars(A)` because a class's dictionary is a read-only `mappingproxy` carrying the compiler's own bookkeeping alongside `x`;
the instance dictionary is a plain `dict` holding only what the code assigned.

A method is a class attribute like any other.
`def show(self):` in a class body stores a function object in the class dictionary,
and `a.show()` finds it by the same fallback that found `a.x`:
nothing on the instance, so look at the class.
That is why `display_object()` reports attributes and methods separately even though both live in the same dictionary,
and why assigning `a.show = something` would shadow the method for `a` alone.

One kind of class attribute does not follow that lookup rule.
A `@property` from [Classes](07_Classes.md#properties)
owns its name on the class,
so reading calls its getter and assigning calls its setter,
and neither one touches the instance dictionary.
The rest of this chapter is about ordinary values stored in a class body.

A class attribute reads like a default right up until someone assigns to an attribute of the same name on one instance.
After that, changing the class attribute changes the value for every object that has not shadowed it,
and leaves the one that has behind.
The bug surfaces far from the line that caused it.

The shadowing rule protects you only while the shared value is immutable:

```python
# shared_mutable.py

class Cart:
    items: list[str] = []  # One list, shared by every Cart

a, b = Cart(), Cart()
a.items.append("apple")  # Mutates, does not assign
print(a.items, b.items)
#: ['apple'] ['apple']
a.items = ["pear"]  # Assignment shadows, as before
print(a.items, b.items)
#: ['pear'] ['apple']
```

`a.items.append("apple")` never assigns to `a.items`.
It reads `items`, finds nothing on `a`, falls back to the class,
and mutates the one list stored there.
The mutation creates no instance attribute, so `b` sees the apple too.
The next line does assign,
which creates `a.items` on the instance and shadows the class list,
leaving `b` still reading the shared one.
Reading is the half with no protection.
`a.items` is a read, so it reaches the shared list,
and `.append()` then mutates the object every instance is reading.
Only assignment makes an instance its own copy, and this line never assigns.
A type checker cannot help here either,
since `a.items.append("apple")` is a correct call on a `list[str]`.
[Real Per-Object Defaults](#real-per-object-defaults),
at the end of this chapter, gives each object its own value instead.
A mutable one belongs in a `@dataclass` field with a `default_factory`,
covered in [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes).

## Declaring Shared State with ClassVar

When you genuinely want one shared value, say so with `ClassVar` from `typing`.
The checker then treats it as class-wide,
and rejects a direct assignment through an instance that would shadow it:

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
# a.total = 99  # ty: Cannot assign to ClassVar `total`
```

`display_object(Tally)` shows what the class holds: `total`,
and nothing called `label`.
An assignment in the class body creates a class attribute,
as `class_attribute_confusion.py` showed above.
`total: ClassVar[int] = 0` has the `= 0`,
so it exists on `Tally` before any instance exists.
`label: str` has no `=`, so the class stores nothing under that name.
The annotation only records, in `Tally.__annotations__`,
that a `Tally` will eventually carry a `label`.
That declaration is invisible to `display_object()`,
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

### A Bare Annotation Declares, It Does Not Create

A *bare annotation*, one with no assigned value,
is a declaration rather than a placeholder.
It states that instances of this class will carry a `label` attribute of type `str`,
set somewhere.
Here that somewhere is `__init__()`,
and its `self.label = label` produced the attribute `display_object(a)` found above.
If `__init__()` never assigns it, no attribute exists,
on the instance or the class.
The checker does not catch the omission,
because it trusts the annotation instead of verifying that some method sets it.
The failure surfaces later,
as an `AttributeError` from the first code that reads the missing `label`.

The annotation on `label` is not required here.
If you delete it, `ty` still infers `label: str` correctly from `self.label = label`,
because the parameter's own type carries through to the attribute it initializes.
The annotation is there for symmetry with `total`,
so both names read together at the top instead of one hiding inside the constructor.
[Simulation](38_Simulation.md#a-robot-in-a-maze)
shows the case where the annotation is not optional.
There, code outside the class sets the attribute,
and a bare annotation is the checker's only way to know its type.

### What `ClassVar` Catches

`ClassVar` is a hint for the checker.
It records that `total` belongs to the class,
and it catches the accidental shadowing from the earlier example before it happens.
Python's own attribute lookup ignores it.
One library does read it at runtime:
`@dataclass` leaves a `ClassVar` field out of the constructor it generates,
shown in [Data Classes as Types](12_Data_Classes_as_Types.md#d-a-real-classvar).

`ClassVar` does not catch every form of shadowing:

```python
# counter_near_miss.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        self.total += 1

a, b = Tally(), Tally()
print(a.total, b.total, Tally.total)
#: 1 1 0
```

`self.total += 1` expands to `self.total = self.total + 1`.
The read falls back to the class and finds `0`;
the write lands on the instance and creates a fresh `total` there.
Every `Tally` counts itself once and the shared counter never moves,
which is why `class_var.py` writes `Tally.total += 1` with the class name spelled out.
`ClassVar` does not save you here.
`ty` rejects a direct `self.total = 5`, but it passes the augmented form,
so the one mistake you are most likely to make is the one the checker misses.

Shared storage is not a mistake when sharing is the intent.
A count of every object created, a registry mapping names to classes,
and a constant that all instances read but none change are all class attributes,
and all are clearer with `ClassVar` on them.
`Tally.total` is the first of these.
For the third, a class-level constant,
`Final[int]` says more than `ClassVar[int]`:
it declares the value shared *and* not reassignable.
Use `ClassVar` when you intend the shared value to change,
as `Tally.total` does.
The bug is not the class attribute;
it is writing one where you meant a per-object default.

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
This is the shadowing rule from the start of the chapter, one level up:
`Left` reads through to `Base` until an assignment gives `Left` its own copy,
the way `a` read through to `Stars` until `a.rating = 1`.
A class body stands to its base class as an instance stands to its class.
`Right` writes `shared = 100` without repeating the annotation.
A subclass overriding a `ClassVar` inherits the declaration along with the name,
so restating `ClassVar[int]` adds nothing.

## Real Per-Object Defaults

For real per-object defaults, write a constructor with default arguments,
or use a `@dataclass`,
which turns the class-attribute syntax into instance attribute defaults.
Each object then gets its own storage:

```python
# real_defaults.py
from dataclasses import dataclass

class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # An instance attribute, one per object

@dataclass
class B:
    x: int = 100  # Becomes a constructor default

a = A()
a.x = -1
print(a.x, A().x)  # The change in a does not leak
#: -1 100
print(B().x, B(7).x)
#: 100 7
print(vars(B)["x"], vars(B())["x"])
#: 100 100
```

Both listings define a class `A` whose `x` starts at `100`,
and the two behave in opposite ways.
In `inside_objects.py` the `100` lives on the class and every instance reads it;
here it is a default argument, and `self.x = x` runs on every construction,
giving each object its own storage before anything can read it.
The difference is not the value but where you write it.
The default value itself is still built once, at definition time
(see [Default and Keyword Arguments](05_Functions.md#default-and-keyword-arguments)),
so a *mutable* default argument brings the sharing straight back.
Nothing can mutate `100`, so it is safe.

A `@dataclass` reads the annotated class-body declarations as a template and generates a constructor from them.
The annotation marks a field.
If you write `x = 100` with no `x: int`, `@dataclass` sees nothing:

```python
# dataclass_no_annotation.py
from dataclasses import dataclass, fields

@dataclass
class B:
    x = 100  # No annotation, so not a field

print(fields(B))
#: ()
b = B()
print(vars(b), b.x)
#: {} 100
b.x = -1
print(vars(b), B().x)  # The same shadowing as Stars
#: {'x': -1} 100
```

The name stays an ordinary shared class attribute,
the generated `__init__()` takes no `x`,
and neither the runtime nor the checker complains.
The class attribute survives the decoration: `vars(B)` still holds `x = 100`.
What changes is the generated `__init__()`,
which assigns `self.x` on every instance,
so each object shadows the class attribute at construction and never reads the shared one.
That is why assigning `x` on one `B` cannot leak into a later `B()`,
while `a.rating = 1` on `Stars` left `b` reading a value someone else could change.
[Data Classes as Types](12_Data_Classes_as_Types.md#data-classes)
covers the details.

## Which Dictionary?

Every attribute question in this chapter reduces to one:
which dictionary did the value land in?
Assignment answers it,
and assignment through `self` and assignment through the class name give different answers.
Decide which you want, then write the spelling that says so:
`ClassVar` for shared,
a constructor default or a `@dataclass` field for per-object.

## Exercises

1.  In `class_attribute_confusion.py`,
    add a third instance `c = Stars()` after the `Stars.rating = 9` line,
    and print `c.rating`.
    Predict its value before running,
    then explain why it differs from `a.rating`.
2.  In `class_var_inheritance.py`,
    add a third subclass `class Middle(Base): pass` (no override, like `Left`)
    and print `Middle.shared` alongside the others at each step.
    Confirm `Middle` tracks `Base` the way `Left` does.
3.  In `real_defaults.py`, create `b = B()` and assign `b.x = -1`.
    Then create a second instance, `b2 = B()`,
    and confirm `b2.x` is still `100`, unaffected.
4.  Rewrite `Tally` from `class_var.py` so `total` is a plain (non-`ClassVar`)
    class attribute instead,
    then have an instance assign to `self.total` directly and explain,
    using `vars()` as in `inside_objects.py`, what that assignment creates,
    and where.
5.  Rewrite `Cart` from `shared_mutable.py` as a `@dataclass` with `items: list[str] = field(default_factory=list)`,
    then repeat the `append` and confirm `b.items` stays empty.
    Then try the same class with `items: list[str] = []` and report what `@dataclass` does about it.
6.  In `inside_objects.py`, add `del a.x` after the final `print`,
    then print `vars(a)` and `a.x` again.
    Predict both before running.
    Then run `del a.x` a second time and explain the exception,
    given what `vars(A)` still holds.
7.  In `counter_near_miss.py`,
    print `vars(a)` and `vars(Tally)["total"]` after constructing both instances,
    and use them to explain the `1 1 0` output.
    Then fix the class so the counter actually counts,
    without changing the `ClassVar` declaration,
    and say why `ty` accepted the broken version.
8.  Change `class_var_inheritance.py` so `shared` is `ClassVar[list[int]] = []` and `Left` and `Right` both call `.append()` on it.
    Predict what `Base.shared` holds afterwards, then check.
    Give `Right` its own list with `shared = []` in its body and repeat.
