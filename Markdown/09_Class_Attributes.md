# Class Attributes

How class-level attributes behave surprises programmers coming from C++ or Java.

## Class Attributes Are Not Default Values

A field declared in the class body, outside any method, is a *class attribute*.
It is easy to misread one as a per-object default value.
It is not.
A class attribute creates one shared variable across all instances of the class.
If you then create an instance variable of the same name, that instance variable *shadows* the class attribute.
This trips up programmers coming from C++ or Java,
where storage for such a field is allocated per object before the constructor runs.

Here's an example showing why it can be confusing:

```python
# class_attribute_confusion.py
class Stars:
    rating = 5  # One value, shared by the whole class

a = Stars()
b = Stars()
print(a.rating, b.rating)  # Both read the class attr
#: 5 5
a.rating = 1  # Assigning makes an instance variable on a
print(a.rating, b.rating)  # 'a' shadows it, 'b' sees the class
#: 1 5
Stars.rating = 9  # Change the shared class attr
print(a.rating, b.rating)  # 'a' instance variable, 'b' class attr
#: 1 9
```

An instance and its class each have their own attribute dictionary.
Reading an attribute checks the instance first, then falls back to the class.
Assigning always writes to the instance,
creating an instance variable the first time it is referenced.
To show this we can select the class with `vars(A)` and the instance with `vars(a)`:

```python
# inside_objects.py
class A:
    x = 100  # class attribute

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

So a class attribute seems like a default until someone assigns to an instance variable of the same name.
Changing the class attribute makes the "default" value of `x` seem different for every object that has not shadowed it.
This produces bugs that surface far from their cause.

When you genuinely want one shared value, say so with `ClassVar` from `typing`.
The checker then treats it as class-wide,
and stops you from accidentally creating an instance variable that shadows it:

```python
# class_var.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0  # One shared value, not per-instance
    label: str  # A normal instance variable

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

a = Tally("a")
b = Tally("b")
print(Tally.total)  # Shared by the whole class
#: 2
# a.total = 99  # ty: cannot assign ClassVar "total" via instance
```

`ClassVar` is a hint for the checker, not the runtime.
It records that `total` belongs to the class,
and it catches the accidental shadowing from the earlier example before it happens.

For real per-object defaults, write a constructor with default arguments,
or use a `@dataclass`, which turns the class-attribute syntax into instance variable defaults.
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
This is detailed in [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes).
