# Rethinking Objects: Solutions

## 1. A leaking `tags` list, then plugged

```python
# exercise_1a.py
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Leaky:
    def __init__(
        self, numbers: list[int], tags: list[str]
    ) -> None:
        self._numbers = numbers
        self._bob = Bob()
        self._tags = tags

    @property
    def tags(self) -> list[str]:
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
    def __init__(
        self, numbers: list[int], tags: list[str]
    ) -> None:
        self._numbers = numbers
        self._bob = Bob()
        self._tags = tags

    @property
    def tags(self) -> list[str]:
        return self._tags.copy()

plugged = Plugged([1, 2], ["a", "b"])
plugged.tags.append("z")
print(plugged.tags)
#: ['a', 'b']
```

`.copy()` closes the leak the same way it does for `numbers`: the
caller now mutates a throwaway copy, and `plugged`'s real `_tags`
keeps the items it had. Every new mutable field needs its own
defensive copy. That repetition is the tedium that motivates freezing
the data instead.

## 2. A mutable `Bob` in a frozen data class

```python
# exercise_2.py
from dataclasses import dataclass
from exceptions import expect

@dataclass
class Bob:
    name: str = "Bob"

@dataclass(frozen=True)
class Immutable:
    numbers: tuple[int, ...]
    bob: Bob

immutable = Immutable((1, 2), Bob())
# No error, from ty or from Python:
immutable.bob.name = "Ralph"
print(immutable)
#: Immutable(numbers=(1, 2), bob=Bob(name='Ralph'))
# The mutable Bob makes the instance unhashable
expect(TypeError, hash, immutable)
#: [TypeError] unhashable type: 'Bob'
```

The type checker reports nothing, and Python runs the assignment. `frozen=True` on
`Immutable` blocks rebinding `immutable.bob`. It says nothing about
the object `bob` refers to, and that object is now a mutable `Bob`.
The assignment to `name` assigns to no field of `Immutable`, so none
of the code that `frozen=True` generated runs.

The `hash()` failure shows the same shallowness from another side.
`frozen=True` generates a `__hash__()` that hashes the tuple of field
values, so hashing an `Immutable` hashes its `Bob`. A data class that
compares by value and is not frozen has its `__hash__` set to `None`:
a hash computed from fields that can change would lose the object
inside a dict. Restoring `frozen=True` on `Bob` removes the mutation
and the hash failure together, the clue that they are one problem: a
frozen wrapper around a mutable value. `frozen_leaky.py` shows the same
two symptoms for a `list` field.

Nothing enforces deep immutability, and that is the answer: taking
immutability all the way down is the author's job, one field at a time.
Declare `tuple` rather than `list`, `frozenset` rather than `set`,
`frozendict` rather than `dict`, and a frozen data class rather than a
mutable one for any nested value. The type checker will hold you to
those declarations once you write them. It will not choose them for
you.

## 3. `NewType` at the protocol boundary

```python
# exercise_3.py
from typing import NewType, Protocol
from record import record

Price = NewType("Price", float)
Weight = NewType("Weight", float)

class Priced(Protocol):
    def total(self) -> Price: ...

class Weighted(Protocol):
    def total(self) -> Weight: ...

@record
class Package:
    weight_kg: float

    def total(self) -> Weight:
        return Weight(self.weight_kg)

def charge(item: Priced) -> float:
    return item.total()

package = Package(4.5)
print(charge(package))  # type: ignore
#: 4.5
```

Without the `# type: ignore` on the last line, `ty` rejects the call:

```
error[invalid-argument-type]: Argument to function `charge` is incorrect
  --> exercise_3.py:25:14
   |
25 | print(charge(package))
   |              ^^^^^^^ Expected `Priced`, found `Package`
info: type `Package` is not assignable to protocol `Priced`
info: └── protocol member `total` is incompatible
info:     └── incompatible return types: `Weight` is not assignable to `Price`
```

The comment lets the listing pass the book's type check while the call
still runs and prints `4.5`.

The structural match still holds: `Package.total()` still takes no
arguments and still returns a float at runtime. The two `NewType`
declarations add a distinction the shapes never carry, so the type
checker can finally see that a weight is not a price.

If someone deletes the annotations, the program behaves as it does
now. It prints `4.5` and charges the customer for a number of kilograms.
`NewType` exists only for the type checker: `Weight(2.5)` returns the
`float` `2.5`, and no wrapper survives to run time. The distinction is
real in the source and absent in the process, and that split is the
bargain the chapter describes.

## 4. A `Triple`, adapted by composition

```python
# exercise_4.py
from math import sqrt
from typing import Protocol
from record import record

class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...

def distance(a: Coord, b: Coord) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

@record
class Triple:
    a: float
    b: float
    c: float

@record
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
the two properties `distance()` reads, ignoring `c`. `distance()` stays
as it is, because it asks for `.x` and `.y` alone. `TripleCoord`
supplies that shape, the same way `PairCoord` adapts `Pair`.

## 5. Adding `Square` to the closed `Shape` union

```python
# exercise_5.py
import math
from typing import assert_never
from record import record

@record
class Rectangle:
    length: float
    width: float

@record
class Circle:
    radius: float

@record
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
matching `case`. With the two lines of the `Square` case commented
out, `ty` reports:

```
error[type-assertion-failure]: Argument does not have asserted type `Never`
  --> exercise_5.py:30:13
   |
30 |             assert_never(shape)
   |             ^^^^^^^^^^^^^-----^
   |                          |
   |                          Inferred type of argument is `Square & ~Rectangle & ~Circle`
info: `Never` and `Square & ~Rectangle & ~Circle` are not equivalent types
```

The inferred type names the missing case. The first two `case` lines
rule out `Rectangle` and `Circle`, so the value that arrives at
`case _` is a `Square` that is neither of them, and `assert_never()`
requires `Never`, the type with no values. That report is the
exhaustiveness check the closed union delivers. A missed case becomes
a type error instead of a runtime failure.

## 6. A `NullCache`, following `NullLogger`'s shape

```python
# exercise_6.py
from typing import Protocol

class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...

class NullCache:
    def get(self, key: str) -> str | None:
        return None

    def set(self, key: str, value: str) -> None:
        pass

nc = NullCache()
nc.set("a", "apple")
print(nc.get("a"))
#: None
```

`NullCache` is neutral the same way `NullLogger` is: `set()` does
nothing, and `get()` always reports "not found." A function that takes
an optional cache can take a required `Cache` instead, defaulting to a
shared `NullCache()` instance, so no code that uses the cache needs an
`is None` branch on the cache. The `None` that `get()` returns is a
different matter. A miss is information the caller acts on, so it stays
in the return type.

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
`+=` and `*=`. A future CPython could add another. The override of
`__setitem__()` leaves its parameters unannotated because `list`
overloads that method, once for an index and once for a slice, and the
counter treats both alike.

`CountingBox` reports `3 3 1` because no inherited route into the
list exists. The class holds a list rather than being one, so every
mutation goes through a method this class wrote. Nothing inherited can
bypass a counter that nothing inherited knows about.

The trade is explicit. `CountingList` gets `sort()`, `index()`,
`__len__()`, slicing, and everything else `list` offers, and gets the
counting wrong. `CountingBox` gets only the methods you write for it,
and a caller who wants `sort()` waits until you write one. That is the
choice composition asks you to make on purpose, instead of discovering
later that inheritance made it for you.

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

`fill()` assumes a `Stack` whose `push()` always succeeds, so the fix
keeps that guarantee. `BoundedStack.push()` accepts every item and
discards the oldest to stay inside the limit. Callers who care about
the limit ask `full()` before pushing. `fill()` now runs on both
classes without an exception.

You gave up the refusal. The original `BoundedStack` guarantees that
it never accepts more than two items. This one guarantees only that it
never *keeps* more than two. A caller who pushes five items loses three
of them silently, and `fill()` returns 2 where a caller counting on
`Stack` expects 5. That loss is the right behavior for a ring buffer of
recent events and the wrong behavior for a queue of work that must keep
every item. If `Stack`'s contract includes "every pushed item stays,"
this version still breaks it.

Should `BoundedStack` have been a subclass at all? Probably not. The
two versions of this exercise are the two ways out of the same bind:
either weaken the guarantee until it fits the base contract, or admit
that "a stack that can refuse" is a different type. A separate class
states that difference, with its own `push()` returning `bool` or
raising an exception. Nothing then hands that class to a `fill()`
written for a different contract. Inheritance is a claim about
substitutability, and this class makes a claim it cannot keep.
