# Rethinking Objects: Solutions

## 1. A leaking `tags` list, then plugged

```python
# exercise_1a.py
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Leaky:
    def __init__(self, numbers, tags):
        self._numbers = numbers
        self._bob = Bob()
        self._tags = tags

    @property
    def tags(self):
        return self._tags

leaky = Leaky([1, 2], ["a", "b"])
leaky.tags.append("z")
print(leaky.tags)
#: ['a', 'b', 'z']
```

`tags` leaks for the same reason `numbers` does: the getter hands back
a reference to the real internal list, so appending to what it returns
mutates `Leaky`'s own state from outside.

```python
# exercise_1b.py
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Plugged:
    def __init__(self, numbers, tags):
        self._numbers = numbers
        self._bob = Bob()
        self._tags = tags

    @property
    def tags(self):
        return self._tags.copy()

plugged = Plugged([1, 2], ["a", "b"])
plugged.tags.append("z")
print(plugged.tags)
#: ['a', 'b']
```

`.copy()` closes the leak the same way it does for `numbers`: the
caller now mutates a throwaway copy, and `plugged`'s real `_tags` is
untouched. Every new mutable field needs this same defensive copy
repeated. This is the tedium that motivates freezing the data instead.

## 2. A mutable field in a frozen data class

```python
# exercise_2.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Immutable:
    numbers: list[int]

data = Immutable([1, 2])
data.numbers.append(999)  # No error, from ty or from Python
print(data)
#: Immutable(numbers=[1, 2, 999])
try:
    data.numbers = [3]  # type: ignore
except Exception as e:
    print(type(e).__name__)
#: FrozenInstanceError
```

`ty` reports nothing. `frozen=True` blocks rebinding a field, which is
why the assignment raises `FrozenInstanceError`, and it says nothing at
all about what the field refers to. The `append()` never assigns to
`data.numbers`, so nothing the decorator generated is involved.

Nobody enforces it, which is the answer: making immutability go all the
way down is the author's job, one field at a time. Declare `tuple`
rather than `list`, `frozenset` rather than `set`, `frozendict` rather
than `dict`, and a frozen data class rather than a mutable one for any
nested value. The type checker will hold you to those declarations once
you write them; it will not choose them for you.

## 3. `NewType` at the protocol boundary

```python
# exercise_3.py
from typing import NewType, Protocol

Price = NewType("Price", float)
Weight = NewType("Weight", float)

class Priced(Protocol):
    def total(self) -> Price: ...

class Package:
    def total(self) -> Weight:
        return Weight(2.5)

def charge(item: Priced) -> str:
    return f"${item.total():.2f}"

print(charge(Package()))  # type: ignore
#: $2.50
```

`ty` now rejects the call:

```
error[invalid-argument-type]: Argument to function `charge` is incorrect
info: type `Package` is not assignable to protocol `Priced`
info: └── protocol member `total` is incompatible
info:     └── incompatible return types: `Weight` is not assignable to `Price`
```

The structural match is unchanged: `Package.total()` still takes no
arguments and still returns a float at runtime. What the two `NewType`
declarations add is a distinction the shapes never carried, so the
checker can finally see that a weight is not a price.

Delete the annotations and the program behaves exactly as it does now.
It prints `$2.50` and charges the customer for a number of kilograms,
because `NewType` exists only for the checker: `Weight(2.5)` returns the
`float` `2.5` and no wrapper survives to run time. The distinction is
real in the source and absent in the process, which is the whole bargain
the chapter describes.

## 4. A `Triple`, adapted by composition

```python
# exercise_4.py
from dataclasses import dataclass
from math import sqrt
from typing import Protocol

class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...

def distance(a: Coord, b: Coord) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

@dataclass(frozen=True)
class Triple:
    a: float
    b: float
    c: float

@dataclass(frozen=True)
class TripleCoord:
    triple: Triple

    @property
    def x(self) -> float:
        return self.triple.a

    @property
    def y(self) -> float:
        return self.triple.b

print(distance(TripleCoord(Triple(3, 0, 99)),
               TripleCoord(Triple(0, 4, -1))))
#: 5.0
```

`Triple` has fields `a`, `b`, `c`, none named `x` or `y`, and `c` is
irrelevant to a 2D distance. `TripleCoord` wraps a `Triple` and exposes
only the two properties `distance()` actually needs, ignoring `c`
entirely. `distance()` itself never changes: it only ever asked for
`.x` and `.y`, and `TripleCoord` supplies that shape, the same
way `PairCoord` adapted `Pair`.

## 5. Adding `Square` to the closed `Shape` union

```python
# exercise_5.py
import math
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Rectangle:
    length: float
    width: float

@dataclass(frozen=True)
class Circle:
    radius: float

@dataclass(frozen=True)
class Square:
    side: float

type Shape = Rectangle | Circle | Square

def area(shape: Shape) -> float:
    match shape:
        case Rectangle(length=length, width=width):
            return length * width
        case Circle(radius=radius):
            return math.pi * radius**2
        case Square(side=side):
            return side * side
        case _:
            assert_never(shape)

shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0), Square(5.0)]
for shape in shapes:
    print(round(area(shape), 4))
#: 3.1416
#: 12.0
#: 25.0
```

`ty check` passes because every member of the `Shape` union now has a
matching `case`. Commenting out the `Square` case makes the `match`
non-exhaustive: the checker can prove that a `Square` argument
falls through every `case` to `case _`, which calls `assert_never(shape)`.
Since `shape` could genuinely be a `Square` at that point, the checker
reports that `assert_never()`'s argument is not the `Never` type it
requires, exactly the exhaustiveness check the union was added for. It
turns a missed case into a caught type error instead of a silent
`None` or a runtime crash.

## 6. A `NullCache`, following `NullLogger`'s shape

```python
# exercise_6.py
from typing import Protocol

class Cache(Protocol):
    def get(self, key: str) -> object | None: ...
    def set(self, key: str, value: object) -> None: ...

class NullCache:
    def get(self, key: str) -> object | None:
        return None

    def set(self, key: str, value: object) -> None:
        pass

nc = NullCache()
nc.set("a", 1)
print(nc.get("a"))
#: None
```

`NullCache` is neutral the same way `NullLogger` is: `set()` does
nothing, and `get()` always reports "not found," so a function that
takes an optional cache can take a required `Cache` instead, defaulting
to a shared `NullCache()` instance, with no `is None` branch anywhere
that uses it.
