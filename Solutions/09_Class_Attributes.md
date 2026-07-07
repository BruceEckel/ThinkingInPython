# Class Attributes: Solutions

## 1. A third instance created after the class attribute changes

```python
# exercise_1.py
class Stars:
    rating = 5

a = Stars()
b = Stars()
a.rating = 1       # Shadows the class attribute on 'a' only
Stars.rating = 9   # Changes the shared class attribute
c = Stars()
print(c.rating)
#: 9
```

`c` is a brand-new instance with no instance attribute of its own, so
reading `c.rating` falls through to the class attribute, which is now
`9`. It differs from `a.rating` (still `1`) because `a` got its own
shadowing instance attribute back when `a.rating = 1` ran, before
`Stars.rating` was changed to `9`. `c` never shadowed anything, so it
simply sees whatever the class attribute currently holds.

## 2. A third subclass with no override

```python
# exercise_2.py
from typing import ClassVar

class Base:
    shared: ClassVar[int] = 0

class Left(Base):
    pass

class Middle(Base):
    pass

class Right(Base):
    shared = 100  # Its own class attr, separate from Base's

print(Left.shared, Middle.shared, Right.shared)
#: 0 0 100
Base.shared = 9
print(Left.shared, Middle.shared, Right.shared)
#: 9 9 100
Left.shared = 5
print(Base.shared, Left.shared, Middle.shared, Right.shared)
#: 9 5 9 100
```

`Middle` behaves exactly like `Left`: neither declares its own
`shared`, so both track `Base.shared` through the normal attribute
lookup chain, right up until something assigns to `Left.shared` or
`Middle.shared` directly. `Right` is unaffected throughout, because it
created its own separate class attribute the moment it wrote `shared =
100` in its class body.

## 3. A second `B()` instance is unaffected by the first

```python
# exercise_3.py
from dataclasses import dataclass

@dataclass
class B:
    x: int = 100  # Constructor default, not class attribute

b = B()
b2 = B()
b.x = -1
print(b.x, b2.x)
#: -1 100
```

Each call to `B()` runs the generated `__init__()`, which assigns `100`
to `self.x` as a fresh instance variable for that particular object.
`b.x = -1` only touches `b`'s own attribute; `b2` was constructed
independently and keeps its own `100`. This is the same guarantee
`real_defaults.py` demonstrates with `A`: a constructor default
creates one value per instance, unlike a class-body attribute, which
creates one value shared by all instances until something shadows it.

## 4. A plain class attribute masquerading as shared state

```python
# exercise_4.py
class Tally:
    total = 0  # Plain class attribute, no ClassVar
    label: str

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

a = Tally("a")
b = Tally("b")
print(Tally.total)
#: 2
a.total = 99  # This does NOT touch Tally.total
print(vars(a))
#: {'label': 'a', 'total': 99}
print(Tally.total)
#: 2
```

`a.total = 99` looks like it should update the shared count, but
assignment always writes to the instance, never the class. It creates
a brand-new instance attribute named `total` on `a`, which then
shadows `Tally.total` for `a` specifically. `vars(a)` shows this
directly: `a` now has its own `total` entry. `Tally.total`, read
through the class, is completely untouched and still reports `2`.
This is precisely the shadowing bug `ClassVar` exists to catch. Had
`total` been declared `total: ClassVar[int] = 0`, the type checker
would flag `a.total = 99` as an error before this line ever ran,
because it can see this assignment would create this confusing shadow.
