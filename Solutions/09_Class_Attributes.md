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
b.x = -1
b2 = B()
print(b.x, b2.x)
#: -1 100
```

Each call to `B()` runs the generated `__init__()`, which assigns `100`
to `self.x` as a fresh instance attribute for that particular object.
`b.x = -1` only touches `b`'s own attribute. `b2` was constructed
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
This is precisely the shadowing bug `ClassVar` exists to catch. If
`total` is declared `total: ClassVar[int] = 0`, the type checker
flags `a.total = 99` as an error before this line ever runs,
because it can see this assignment creates this confusing shadow.

## 5. A per-instance list, via `default_factory`

```python
# exercise_5.py
from dataclasses import dataclass, field

@dataclass
class Cart:
    items: list[str] = field(default_factory=list)

a, b = Cart(), Cart()
a.items.append("apple")
print(a.items, b.items)
#: ['apple'] []
```

`default_factory=list` calls `list()` once per construction, so the
generated `__init__()` assigns a brand-new list to `self.items` on
every `Cart`. Each object owns its list from birth, and `a`'s append
cannot reach `b`.

Writing the same class with a bare `items: list[str] = []` does not
produce the shared-list bug, because `@dataclass` refuses to build the
class at all:

```python
# exercise_5_rejected.py
from dataclasses import dataclass

try:
    @dataclass
    class Cart:
        items: list[str] = []

except ValueError as e:
    print(type(e).__name__)
    print(str(e).partition(" for ")[0])
#: ValueError
#: mutable default <class 'list'>
```

The full message ends with the remedy: `use default_factory`. The
error arrives at class-definition time, not at first use, and it
names the fix. `@dataclass` can detect the mistake because it inspects
every default before generating the constructor. A plain class body,
as `shared_mutable.py` showed, has nobody doing that inspection.

## 6. `del` unshadows, once

```python
# exercise_6.py
class A:
    x = 100

a = A()
a.x = 1
print(vars(a), a.x)
#: {'x': 1} 1
del a.x
print(vars(a), a.x)
#: {} 100
try:
    del a.x
except AttributeError as e:
    print(type(e).__name__, e)
#: AttributeError 'A' object has no attribute 'x'
```

`del a.x` removes the entry from the instance dictionary, which is
the only place assignment ever wrote. `vars(a)` is empty again, and
`a.x` reads `100`, because the lookup falls through to the class the
way it did before any assignment. Nothing was lost: the class
attribute was never touched in either direction.

The second `del a.x` fails because there is nothing left on the
instance to delete. `del` does not follow the same fallback path that
reading does, so it never reaches `vars(A)["x"]`, which still holds
`100`. Deleting a class attribute takes `del A.x`, naming the class,
the same asymmetry as assignment: reads fall back to the class,
writes and deletes do not.

## 7. Why `self.total += 1` leaves the class counter at zero

```python
# exercise_7.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        self.total += 1  # type: ignore

a, b = Tally(), Tally()
print(a.total, b.total, Tally.total)
#: 1 1 0
print(vars(a), vars(Tally)["total"])
#: {'total': 1} 0

class Counting:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        Counting.total += 1  # Name the class, not self

c, d = Counting(), Counting()
print(c.total, d.total, Counting.total)
#: 2 2 2
print(vars(c), vars(Counting)["total"])
#: {} 2
```

`vars(a)` holds `{'total': 1}` and the class still holds `0`, which is
the whole explanation. `self.total += 1` expands to
`self.total = self.total + 1`. The read finds nothing on the instance,
falls back to the class, and gets `0`. The write then goes where every
write through an instance goes: onto the instance. Each object ends up
with its own `total` of `1`, shadowing a class attribute that was never
touched.

The fix names the class on the left. `Counting.total += 1` reads and
writes the same class dictionary, so both instances report `2` and
`vars(c)` is empty: nothing was ever created on an instance, and
`c.total` is the fallback finding the shared value.

With the `# type: ignore` removed, `ty` reports
`invalid-attribute-access`: "Cannot assign to ClassVar `total` from an
instance." The augmented form expands to an assignment through `self`,
and the type checker treats it as it treats `a.total = 99`: a write to a
`ClassVar` through an instance. The declaration catches the mistake at
check time. The listing suppresses the report so it can demonstrate
what the write does when it runs.

## 8. A mutable `ClassVar` shared down the hierarchy

```python
# exercise_8.py
from typing import ClassVar

class Base:
    shared: ClassVar[list[int]] = []

class Left(Base):
    pass

class Right(Base):
    pass

Left.shared.append(1)
Right.shared.append(2)
print(Base.shared, Left.shared, Right.shared)
#: [1, 2] [1, 2] [1, 2]
print(Left.shared is Base.shared)
#: True

class Base2:
    shared: ClassVar[list[int]] = []

class Left2(Base2):
    pass

class Right2(Base2):
    shared = []  # Its own list, separate from Base2's

Left2.shared.append(1)
Right2.shared.append(2)
print(Base2.shared, Left2.shared, Right2.shared)
#: [1] [1] [2]
```

`Base.shared` holds `[1, 2]`, and so do both subclasses, because there
is only one list. Neither `Left` nor `Right` declared its own, so both
names resolve up to `Base`, and `.append()` mutates what it finds
there. `Left.shared is Base.shared` proves they are one object rather
than three that happen to be equal.

This is section 1's mutable-value trap and section 3's inheritance rule
meeting. Each is harmless on its own: an immutable `ClassVar` survives
inheritance because nothing can change it in place, and a mutable one
in a single class at least keeps the sharing visible. Together they
produce a base-class list that every subclass writes to and none of
them declared.

Giving `Right2` its own `shared = []` splits it off, and only it. The
assignment in the class body creates a new entry in `Right2`'s own
dictionary, so `Right2.shared` stops resolving up, while `Left2` still
shares `Base2`'s list. The result, `[1] [1] [2]`, is the same
one-per-class-that-declares-it pattern the integer version showed.

The real bug this models is a registry on a base class. Every subclass
appends its own entry, and they all land in one list nobody meant to
share. The fix is the one the chapter gives for instances: build the
mutable value per owner rather than once in the class body, with
`__init_subclass__()` giving each subclass its own, or a
`default_factory` field giving each instance its own.
