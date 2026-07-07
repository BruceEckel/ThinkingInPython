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

## 2. A third point confirming both versions agree

```python
# exercise_2.py
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

def distance(a: Point, b: Point) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

p1, p2 = Point(3, 0), Point(0, 4)
p3 = Point(6, 8)
print(distance(p1, p3))
#: 8.54400374531753
print(p1.distance_to(p3))
#: 8.54400374531753
```

The free function and the method compute the identical formula on the
identical data, so they agree on any pair of points, not only the
original `3-4-5` example. Nothing about adding a third point requires
touching either `distance()` or `distance_to()`.

## 3. A `Triple`, adapted by composition

```python
# exercise_3.py
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

## 4. Adding `Square` to the closed `Shape` union

```python
# exercise_4.py
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
non-exhaustive: the checker can prove that a `Square` argument would
fall through every `case` to `case _`, which calls `assert_never(shape)`.
Since `shape` could genuinely be a `Square` at that point, the checker
reports that `assert_never()`'s argument is not the `Never` type it
requires, exactly the exhaustiveness check the union was added for. It
turns a missed case into a caught type error instead of a silent
`None` or a runtime crash.

## 5. A `NullCache`, following `NullLogger`'s shape

```python
# exercise_5.py
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
