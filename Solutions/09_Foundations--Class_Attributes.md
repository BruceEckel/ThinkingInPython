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
reading `c.rating` falls back to the class attribute, which is now
`9`. `c.rating` differs from `a.rating` (still `1`) because `a` got
its own shadowing instance attribute when `a.rating = 1` ran, before
`Stars.rating = 9` ran. `c` never shadowed anything, so it sees
whatever the class attribute currently holds.

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
`Middle.shared` directly. `Right` holds `100` throughout, because it
created its own separate class attribute the moment its class body ran
`shared = 100`.

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
`b.x = -1` only touches `b`'s own attribute. `b2` came from its own
`B()` call and keeps its own `100`. `real_defaults.py` demonstrates
the same guarantee with `A`: a constructor default creates one value
per instance, unlike a class-body attribute, which creates one value
shared by all instances until something shadows it.

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
assignment through an instance always writes to the instance, never
the class. That assignment creates a brand-new instance attribute
named `total` on `a`, which then shadows `Tally.total` for `a`
specifically. `vars(a)` shows the shadow directly: `a` now has its
own `total` entry. `Tally.total`, read through the class, still
reports `2`, because nothing wrote to the class. This shadow is
precisely the bug `ClassVar` exists to catch. Declare `total:
ClassVar[int] = 0` instead, and the type checker flags `a.total = 99`
as an error before the line ever runs, because it can see the
assignment would create this shadow.

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

`@dataclass` refuses to build the same class written with a bare
`items: list[str] = []`, so the shared-list bug never gets a chance to
appear:

```python
# exercise_5_rejected.py
from dataclasses import dataclass

try:
    @dataclass
    class Cart:
        items: list[str] = []

except ValueError as e:
    print(str(e).partition(" is not")[0])
    print(str(e).partition(" for ")[0])
#: mutable default <class 'list'> for field items
#: mutable default <class 'list'>
```

The error arrives at class-definition time, not at first use, and
the full message ends with the remedy: `use default_factory`.
`@dataclass` can detect the mistake because it inspects every default
before generating the constructor. Nobody inspects a plain class body,
which is why `shared_mutable.py`'s `Cart` built without complaint.

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
`a.x` reads `100`, because the lookup falls back to the class the
way it did before any assignment. The class attribute kept its `100`
throughout: the assignment and the `del` both stayed on the instance.

The second `del a.x` fails because the instance dictionary is empty.
`del` stops at the instance, the way assignment does, so
`vars(A)["x"]` keeps its `100`. Deleting the class attribute takes
`del A.x`, naming the class. The asymmetry is the same one assignment
has: reads fall back to the class, writes and deletes do not.

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

`vars(a)` holds `{'total': 1}` and the class still holds `0`, and
those two facts are the whole explanation. `self.total += 1` expands to
`self.total = self.total + 1`. The read finds nothing on the instance,
falls back to the class, and gets `0`. The write then goes where every
write through an instance goes: onto the instance. Each object ends up
with its own `total` of `1`, shadowing a class attribute that still
holds `0`.

The fix names the class on the left. `Counting.total += 1` reads and
writes the same class dictionary, so both instances report `2`.
`vars(c)` is empty because the constructor wrote only to the class,
and `c.total` is the read falling back to that shared value.

With the `# type: ignore` removed, `ty` reports
`invalid-attribute-access`: "Cannot assign to ClassVar `total` from an
instance." The augmented form expands to an assignment through `self`,
and the type checker treats that assignment the way it treats
`a.total = 99`: a write to a `ClassVar` through an instance. The
`ClassVar` declaration catches the mistake at check time. The listing
suppresses the report so it can demonstrate
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

`Base.shared` holds `[1, 2]`, and so do both subclasses, because all
three names share one list. Neither `Left` nor `Right` declared its
own, so both names read through to `Base`, and `.append()` mutates
what it finds there. `Left.shared is Base.shared` proves they are one
object rather than three that happen to be equal.

Here the mutable-value trap of `shared_mutable.py` meets the
inheritance rule of `class_var_inheritance.py`. Each is harmless on
its own: an immutable `ClassVar` survives inheritance because nothing
can change it in place, and a mutable one in a single class keeps the
sharing visible. Together they produce a base-class list that every
subclass writes to and none of them declared.

Giving `Right2` its own `shared = []` splits it off, and only it. The
assignment in the class body creates a new entry in `Right2`'s own
dictionary, so `Right2.shared` stops reading through to `Base2`,
while `Left2` still shares `Base2`'s list. The result, `[1] [1] [2]`,
follows the same rule the integer `shared` in exercise 2 showed: one
value per class that declares it.

The real bug this listing models is a registry on a base class. Every
subclass appends its own entry, and the entries all land in one list
nobody meant to share. The fix is the chapter's: build the mutable
value per owner rather than once in the class body. A
`default_factory` field gives each instance its own list, and
`__init_subclass__()` gives each subclass its own.
