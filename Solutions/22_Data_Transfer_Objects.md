# Data Transfer Objects: Solutions

## 1. Two `Messenger`s do not share attributes

```python
# exercise_1.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m1: Any = Messenger(info="hi", count=3)
m2: Any = Messenger(name="Bob", age=30)
print(m1.info, m1.count)
#: hi 3
print(m2.name, m2.age)
#: Bob 30
print(hasattr(m1, "name"), hasattr(m2, "info"))
#: False False
```

Each `Messenger()` call assigns a fresh `dict` (the one `**kwargs`
built from that call's own arguments) to that instance's `__dict__`.
Every instance gets its own independent dictionary, unlike a class
attribute from [Class Attributes](09_Class_Attributes.md), which is
one object shared by every instance until something shadows it. `m1`
and `m2` share nothing: `m1` has no `name`, and `m2` has no `info`.

## 2. A third field on `Point`

```python
# exercise_2.py
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

p = Point(1.0, 2.0, 3.0)
print(p)
#: Point(x=1.0, y=2.0, z=3.0)
p.x = 3.5
print(p == Point(3.5, 2.0, 3.0))
#: True
```

`@dataclass` reads whatever fields the class body declares and
generates `__init__()`, `__repr__()`, and `__eq__()` to match. Adding
`z: float` extends the constructor to three positional arguments, the
`repr()` to three fields, and the equality comparison to three values,
with no other code to update.

## 3. A `NamedTuple` called `Fraction`

```python
# exercise_3.py
from typing import NamedTuple

class Fraction(NamedTuple):
    numerator: int
    denominator: int

f = Fraction(3, 4)
print(f)
#: Fraction(numerator=3, denominator=4)
print(f[0], f[1])
#: 3 4
num, denom = f
print(num, denom)
#: 3 4
```

`Fraction` behaves exactly like `Color` does: `f.numerator` and
`f.denominator` are readable by name, `f[0]` and `f[1]` still work
because a `NamedTuple` is still a real tuple underneath, and unpacking
with `num, denom = f` works the same way it would for a plain
`(3, 4)` tuple.

## 4. A fourth attribute supplied at construction

```python
# exercise_4.py
from types import SimpleNamespace

built = SimpleNamespace(info="Spam", b=["x", "y"], more=11,
                        extra="eggs")
print(vars(built))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11, 'extra': 'eggs'}

assigned = SimpleNamespace(info="Spam", b=["x", "y"], more=11)
assigned.extra = "eggs"
print(vars(assigned))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11, 'extra': 'eggs'}

print(vars(built) == vars(assigned))
#: True
```

A keyword argument and a later assignment both add one entry to the
instance's `__dict__`, and `vars()` reads that dict. The two
namespaces are indistinguishable afterward. Even the order matches,
because a dict keeps insertion order and both routes add `extra`
last. If you assign the attributes in a different sequence, the dicts
still compare equal, since dict equality ignores order.
