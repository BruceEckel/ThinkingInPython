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
    print(e)
#: cannot assign to field 'numbers'
try:
    # The list field makes the instance unhashable
    hash(data)
except TypeError as e:
    print(e)
#: unhashable type: 'list'
```

`ty` reports nothing. `frozen=True` blocks rebinding a field, which is
why the assignment raises `FrozenInstanceError`, and it says nothing at
all about what the field refers to. The `append()` never assigns to
`data.numbers`, so nothing the decorator generated is involved.

The `hash()` failure is the same shallowness seen from another side.
`frozen=True` generates a `__hash__()` that hashes the tuple of field
values, so hashing an `Immutable` hashes its `list`, and a `list` has no
hash. The instance the decorator promised was usable as a dict key is
not, and nothing said so until the first `hash()`. With `tuple` restored,
both the mutation and the hash failure go away together, which is the
clue that they were one problem: a frozen wrapper around a mutable
value.

Nobody enforces it, which is the answer: making immutability go all the
way down is the author's job, one field at a time. Declare `tuple`
rather than `list`, `frozenset` rather than `set`, `frozendict` rather
than `dict`, and a frozen data class rather than a mutable one for any
nested value. The type checker will hold you to those declarations once
you write them. It will not choose them for you.

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
type checker can finally see that a weight is not a price.

Delete the annotations and the program behaves exactly as it does now.
It prints `$2.50` and charges the customer for a number of kilograms,
because `NewType` exists only for the type checker: `Weight(2.5)` returns the
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

shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0),
                       Square(5.0)]
for shape in shapes:
    print(round(area(shape), 4))
#: 3.1416
#: 12.0
#: 25.0
```

`ty check` passes because every member of the `Shape` union now has a
matching `case`. Commenting out the `Square` case makes the `match`
non-exhaustive: the type checker can prove that a `Square` argument
falls through every `case` to `case _`, which calls `assert_never(shape)`.
Since `shape` could genuinely be a `Square` at that point, the type checker
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

## 7. Counting every route into the list

```python
# exercise_7.py
from dataclasses import dataclass, field
from typing import override

class CountingList(list[int]):
    def __init__(self) -> None:
        super().__init__()
        self.appends = 0
        self.sets = 0

    @override
    def append(self, item: int, /) -> None:
        self.appends += 1
        super().append(item)

    @override
    def __setitem__(self, index, value) -> None:
        self.sets += 1
        super().__setitem__(index, value)

counted = CountingList()
counted.append(1)
counted.extend([2, 3])  # Past append()
counted[0] = 99  # Counted
counted.insert(0, 7)  # Past both overrides
print(len(counted), counted.appends, counted.sets)
#: 4 1 1

@dataclass
class CountingBox:
    items: list[int] = field(default_factory=list)
    appends: int = 0
    sets: int = 0

    def append(self, item: int) -> None:
        self.appends += 1
        self.items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

    def __setitem__(self, index: int, value: int) -> None:
        self.sets += 1
        self.items[index] = value

box = CountingBox()
box.append(1)
box.extend([2, 3])
box[0] = 99
print(len(box.items), box.appends, box.sets)
#: 3 3 1
```

The subclass counts one append out of three and misses `insert()`
entirely. `extend()` and `insert()` both add elements through `list`'s
own C implementation, which never calls the Python-level `append()` or
`__setitem__()` you overrode. Other routes past the counters include
`+=`, slice assignment, and `list.__init__` with an iterable, and the
list is not fixed: a future CPython could add another.

`CountingBox` reports `3 3 1` because there is no other route. The
class holds a list rather than being one, so every mutation is a method
this class wrote. Nothing inherited can bypass a counter that nothing
inherited knows about.

The trade is explicit. `CountingList` got `sort()`, `index()`,
`__len__()`, slicing, and everything else `list` offers, and got the
counting wrong. `CountingBox` gets nothing it did not write, and a
caller who wants `sort()` has to be given one. That is the choice
composition asks you to make on purpose, instead of discovering later
that inheritance made it for you.

## 8. `BoundedStack` without breaking the contract

```python
# exercise_8.py
from dataclasses import dataclass, field
from typing import ClassVar, override

@dataclass
class Stack:
    items: list[int] = field(default_factory=list)

    def push(self, item: int) -> None:
        self.items.append(item)

@dataclass
class BoundedStack(Stack):
    limit: ClassVar[int] = 2

    # The limit, exposed as a question
    def full(self) -> bool:
        return len(self.items) >= self.limit

    @override
    def push(self, item: int) -> None:  # Always succeeds
        super().push(item)
        del self.items[:-self.limit]  # Drop the oldest

def fill(stack: Stack, count: int) -> int:
    for n in range(count):
        stack.push(n)
    return len(stack.items)

print(fill(Stack(), 5))
#: 5
print(fill(BoundedStack(), 5))  # No exception now
#: 2

bounded = BoundedStack()
bounded.push(1)
print(bounded.full())
#: False
bounded.push(2)
print(bounded.full(), bounded.items)
#: True [1, 2]
```

`fill()` was written against a `Stack` whose `push()` always succeeds,
so the fix keeps that promise. `BoundedStack.push()` accepts every item
and discards the oldest to stay inside the limit, and callers who care
about the limit ask `full()` before pushing. `fill()` now runs on both
classes, which is what substitutability means.

What you gave up is the refusal. The original `BoundedStack` guaranteed
that no more than two items were ever accepted. This one guarantees
only that no more than two are ever *kept*. A caller who pushes five
items loses three of them silently, which is the right behavior for a
ring buffer of recent events and the wrong behavior for a queue of work
that must not be dropped.

Should `BoundedStack` have been a subclass at all? Probably not. The
two versions of this exercise are the two ways out of the same bind:
either weaken the guarantee until it fits the base contract, or admit
that "a stack that can refuse" is a different type. A separate class
with its own `push()` returning `bool`, or raising, is honest about
that, and nothing then hands it to a `fill()` that was never written
for it. Inheritance is a claim about substitutability, and this class
was making a claim it could not keep.
