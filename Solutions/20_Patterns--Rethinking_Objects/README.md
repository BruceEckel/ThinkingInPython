# Rethinking Objects: Solutions

## 1. A leaking `tags` list, then plugged

> In `leaky.py`, add a `tags: list[str]` field to `Leaky`,
> exposed through a `@property` the same way `numbers` is,
> and demonstrate the same leak by mutating the list you get back.
> Then plug the leak the way `plugged.py` plugs `numbers` and `bob`.

<details>
<summary>Where to look</summary>

[Encapsulation Leaks](../../Chapters/20_Patterns--Rethinking_Objects.md#encapsulation-leaks) shows a getter handing out a reference to the real internal list.
Mutate what the `tags` property returns to see the leak.
[Plugging Leaks Is Tedious](../../Chapters/20_Patterns--Rethinking_Objects.md#plugging-leaks-is-tedious) shows the fix: return a copy, so the caller changes only the copy.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1a.py
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Leaky:
    def __init__(
        self, numbers: list[int], tags: list[str]
    ) -> None:
        ...

    @property
    def tags(self) -> list[str]:
        ...
```

```python
# The shape of exercise_1b.py
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Plugged:
    def __init__(
        self, numbers: list[int], tags: list[str]
    ) -> None:
        ...

    @property
    def tags(self) -> list[str]:
        ...
```

<details>
<summary>Solution</summary>

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

**Expose the internal list.** `tags` leaks for the same reason
`numbers` does. The getter hands back a reference to the real internal
list, so appending to what it returns mutates `Leaky`'s own state from
outside.

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

**Isolate the internal list.** `.copy()` closes the leak the same way
it does for `numbers`. The caller now mutates a throwaway copy, and
`plugged`'s real `_tags` keeps the items it had.

Every new mutable field needs its own defensive copy. That repetition
is the tedium that motivates freezing the data instead.

</details>
</details>
</details>

## 2. A mutable `Bob` in a frozen data class

> In `immutable.py`, remove `frozen=True` from `Bob` and leave it on `Immutable`.
> Show that `ty check` still passes,
> that `immutable.bob.name = "Ralph"` now succeeds,
> and that `hash(immutable)` now raises a `TypeError`,
> so the frozen instance can no longer be a dict key.
> Restore the `frozen=True`.
> Who, then, must make immutability go all the way down?

<details>
<summary>Where to look</summary>

[The Immutability Solution](../../Chapters/20_Patterns--Rethinking_Objects.md#the-immutability-solution) explains what `frozen=True` generates for a data class.
Consider which operations it guards: rebinding a field, or changing the object to which the field refers.
The generated `__hash__()` hashes the field values, so look at what it must hash when one value is mutable.

<details>
<summary>Solution</summary>

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

**Mutate past the frozen field.** The type checker reports nothing, and Python runs the assignment. `frozen=True` on
`Immutable` blocks rebinding `immutable.bob`. It says nothing about
the object to which `bob` refers, and that object is now a mutable
`Bob`. The assignment to `name` assigns to no field of `Immutable`,
so none of the code that `frozen=True` generated runs.

**Check hashability.** The `hash()` failure shows the same shallowness from another side.
`frozen=True` generates a `__hash__()` that hashes the tuple of field
values, so hashing an `Immutable` hashes its `Bob`. On a data class
that compares by value and is not frozen, `@dataclass` sets
`__hash__` to `None`. A hash computed from fields that can change
would lose the object inside a dict.

Restoring `frozen=True` on `Bob` removes the mutation and the hash
failure together, the clue that they are one problem: a frozen wrapper
around a mutable value.
`frozen_leaky.py` shows the same two symptoms for a `list` field.

Nothing enforces deep immutability, and that is the answer: taking
immutability all the way down is the author's job, one field at a time.
Declare `tuple` rather than `list`, `frozenset` rather than `set`,
`frozendict` rather than `dict`, and a frozen data class rather than a
mutable one for any nested value. The type checker holds you to
those declarations once you write them. It does not choose them for
you.

</details>
</details>

## 3. `NewType` at the protocol boundary

> In `protocol_collision.py`,
> define `Price = NewType("Price", float)` and `Weight = NewType("Weight", float)`,
> change `Priced.total()` to return a `Price`,
> `Weighted.total()` to return a `Weight`,
> and `Package.total()` to return a `Weight`.
> Run `ty check` and read the error it reports for `charge(package)`.
> Then say what still goes wrong at runtime if someone deletes the annotations.

<details>
<summary>Where to look</summary>

[What the Shape Does Not Say](../../Chapters/20_Patterns--Rethinking_Objects.md#what-the-shape-does-not-say) shows two protocols whose `total()` methods have the same shape.
`NewType` gives each `float` a distinct type, so the type checker can tell a `Price` from a `Weight`.
For the runtime question, consider what `Weight(2.5)` returns when the program runs.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import NewType, Protocol
from record import record

class Priced(Protocol):
    def total(self) -> Price: ...

class Weighted(Protocol):
    def total(self) -> Weight: ...

@record
class Package:
    weight_kg: float

    def total(self) -> Weight:
        ...

def charge(item: Priced) -> float:
    ...
```

<details>
<summary>Solution</summary>

If you change the annotation on `Package.total()` to `Weight` and leave `return self.weight_kg` as it is,
`ty` reports an `invalid-return-type` error on that line: it expected `Weight` and found `float`.
A `float` is not a `Weight` until `Weight()` marks it as one.
The solution wraps the return value in `Weight(...)`, a call that returns the same float at runtime.

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

**Give each meaning its own type.** The runtime shape still matches.
`Package.total()` still takes no arguments and still returns a float
at runtime. The two `NewType` declarations add a distinction the
shapes lack, so the type checker finally sees that a weight is not a
price.

If someone deletes the annotations, the program behaves as it does
now. It prints `4.5` and charges the customer for a number of kilograms.
`NewType` exists only for the type checker. `Weight(2.5)` returns the
`float` `2.5`, and no wrapper survives to run time. The distinction is
real in the source and absent in the process, and that split is the
bargain the chapter describes.

</details>
</details>
</details>

## 4. A `Triple`, adapted by composition

> In `distance_protocol.py`, add a third class, `Triple`, with fields `a`,
> `b`, `c` (no `x` or `y`),
> and an adapter `TripleCoord` that exposes `x` as `a` and `y` as `b`,
> ignoring `c`.
> Confirm `distance()` works on a `TripleCoord` with no change to `distance()`.

<details>
<summary>Where to look</summary>

[Protocols Generalize, Composition Adapts](../../Chapters/20_Patterns--Rethinking_Objects.md#protocols-generalize-composition-adapts) defines the `Coord` protocol and adapts a class that lacks `x` and `y`.
Write `TripleCoord` to hold a `Triple` and expose `x` and `y` as read-only properties that return the fields you choose.
`distance()` needs no change, because it asks only for those two properties.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from math import sqrt
from typing import Protocol
from record import record

class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...

def distance(a: Coord, b: Coord) -> float:
    ...

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
        ...

    @property
    def y(self) -> float:
        ...
```

<details>
<summary>Solution</summary>

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

</details>
</details>
</details>

## 5. Adding `Square` to the closed `Shape` union

> In `shapes_match.py`, add a new shape, `Square(side: float)`,
> to the `Shape` union, add its `case` to `area()`,
> and confirm `ty check` still passes.
> Then temporarily comment out the new `case` and observe what `assert_never()` causes the type checker to report.

<details>
<summary>Where to look</summary>

[Pattern Matching on a Union](../../Chapters/20_Patterns--Rethinking_Objects.md#pattern-matching-on-a-union) shows `area()` matching on each member of a closed union.
Add `Square` to the `type Shape` alias and give `area()` a matching `case` with a class pattern.
The final `case _` calls `assert_never()`, which requires the type `Never`.
Remove your new `case` and read the type the checker reports for its argument.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
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
    ...
```

<details>
<summary>Solution</summary>

If you end the `match` without the `case _` arm, `ty check` still passes on the full listing,
because the three cases cover the union.
Commenting out the `Square` case then draws an `invalid-return-type` error,
which reports that `area()` can implicitly return `None` but names no shape.
The solution keeps `assert_never()` so the report names the missing `Square`.

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

**Check exhaustiveness.** The inferred type names the missing case. The first two `case` lines
rule out `Rectangle` and `Circle`, so the `shape` that arrives at
`case _` is a `Square` that is neither of them, and `assert_never()`
requires `Never`, the type with no values. That report is the
exhaustiveness check the closed union delivers. A missed case becomes
a type error instead of a runtime failure.

</details>
</details>
</details>

## 6. A `NullCache`, following `NullLogger`'s shape

> In `null_logger.py`, write a second null-object style class, `NullCache`,
> whose `get(key)` always returns `None` and whose `set(key, value)` does nothing,
> following the same shape as `NullLogger`.

<details>
<summary>Where to look</summary>

[Null Object](../../Chapters/20_Patterns--Rethinking_Objects.md#null-object) shows `NullLogger` standing in for a real logger with the same methods and neutral behavior.
Declare a `Cache` protocol with `get()` and `set()`, then write `NullCache` to satisfy it.
Its `get()` reports a miss, and its `set()` discards the value.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from typing import Protocol

class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...

class NullCache:
    def get(self, key: str) -> str | None:
        ...

    def set(self, key: str, value: str) -> None:
        ...
```

<details>
<summary>Solution</summary>

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

`NullCache` is neutral the same way `NullLogger` is. `set()` does
nothing, and `get()` always reports "not found." A function that takes
an optional cache can take a required `Cache` instead, defaulting to a
shared `NullCache()` instance, so no code that uses the cache needs an
`is None` branch on the cache. The `None` that `get()` returns is a
different matter. A miss is information on which the caller acts, so
`None` stays in the return type.

</details>
</details>
</details>

## 7. Counting every route into the list

> In `counting_list.py`, count `__setitem__` as well,
> then find a second `list` method that changes the contents without going through either override.
> Rewrite `CountingList` to hold a list instead of inheriting from one,
> and show that the counts are now correct for every route in.

<details>
<summary>Where to look</summary>

[Prefer Composition to Inheritance](../../Chapters/20_Patterns--Rethinking_Objects.md#prefer-composition-to-inheritance) shows `CountingList` missing calls that `list` makes in its own implementation.
Try `extend()` and `insert()` on the subclass and compare the counts with the contents.
The composed version holds a `list` as a field and exposes only methods you write, so every mutation made through the box passes through a counter.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from dataclasses import dataclass, field
from typing import override

class CountingList(list[int]):
    def __init__(self) -> None:
        ...

    @override
    def append(self, item: int, /) -> None:
        ...

    @override
    def __setitem__(self, index, value) -> None:
        ...

@dataclass
class CountingBox:
    items: list[int] = field(default_factory=list)
    appends: int = 0
    sets: int = 0

    def append(self, item: int) -> None:
        ...

    def extend(self, more: list[int]) -> None:
        ...

    def __setitem__(self, index: int, value: int) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you write `CountingBox.extend()` as `self.items.extend(more)`, the box prints `3 1 1`.
The two elements arrive through the held list's own `extend()`, and `appends` misses them.
Composition moves the bug into a class you can read but does not prevent it,
as [Prefer Composition to Inheritance](../../Chapters/20_Patterns--Rethinking_Objects.md#prefer-composition-to-inheritance) notes.
The solution's `extend()` loops over `append()`, so every element passes the counter.

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

**Count item assignment too.** The override of
`__setitem__()` leaves its parameters unannotated because `list`
overloads that method, once for an index and once for a slice, and the
counter treats both alike.

**Find the routes past the overrides.** The subclass counts one append out of three and misses `insert()`
entirely. `extend()` and `insert()` both add elements through `list`'s
own C implementation, which calls neither the Python-level `append()`
nor `__setitem__()` you overrode. Other routes past the counters
include `+=` and `*=`. A future CPython could add another.

**Route every mutation through a counter.** `CountingBox` reports `3 3 1` because no inherited route into the
list exists. The class holds a list rather than being one, so every
mutation that goes through `CountingBox` goes through a method this
class wrote. Nothing inherited
knows the counters exist, so nothing inherited can bypass them.

`CountingList` gets `sort()`, `index()`, `__len__()`, slicing, and
everything else `list` offers, and gets the counting wrong.
`CountingBox` gets only the methods you write for it, and a caller who
needs `sort()` waits until you write one. The trade is the choice
composition asks you to make on purpose, instead of discovering later
that inheritance made it for you.

</details>
</details>
</details>

## 8. `BoundedStack` without breaking the contract

> In `lsp_violation.py`,
> make `BoundedStack` obey the Liskov Substitution Principle without removing the limit:
> keep the base contract that `push()` always succeeds,
> and expose "full" some other way.
> Then say what you gave up,
> and whether `BoundedStack` should be a subclass of `Stack`.

<details>
<summary>Where to look</summary>

[The Liskov Substitution Principle](../../Chapters/20_Patterns--Rethinking_Objects.md#liskov-substitution) shows `fill()` relying on a base `push()` that always succeeds.
Keep that guarantee by having `push()` accept every item and enforce the limit another way, and add a `full()` method callers can ask.
Then decide whether the weaker guarantee is acceptable, and whether a subclass is the right relationship.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from dataclasses import dataclass, field
from typing import ClassVar, override

@dataclass
class Stack:
    items: list[int] = field(default_factory=list)

    def push(self, item: int) -> None:
        ...

@dataclass
class BoundedStack(Stack):
    limit: ClassVar[int] = 2

    # The limit, exposed as a question
    def full(self) -> bool:
        ...

    @override
    def push(self, item: int) -> None:  # Always succeeds
        ...

def fill(stack: Stack, count: int) -> int:
    ...
```

<details>
<summary>Solution</summary>

If you have `push()` return `False` when the stack is full,
`ty` reports an `invalid-method-override` error: `bool` is not assignable to the `None` that `Stack.push()` returns.
`fill()` ignores the return value, so it returns 2 with no sign that three pushes failed.
A refusal by return value is still a refusal,
so the solution's `push()` accepts every item and leaves the question of fullness to `full()`.

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

**Expose the limit as a question.** Callers who care about
the limit ask `full()` before pushing.

**Keep the base guarantee.** `fill()` assumes a `Stack` whose `push()` always succeeds, so the fix
keeps that guarantee. `BoundedStack.push()` accepts every item and
discards the oldest to stay inside the limit. `fill()` now runs on both
classes without an exception.

You gave up the refusal. The original `BoundedStack` guarantees that
it accepts at most two items. This version guarantees only that it
*keeps* at most two. A caller who pushes five items loses three
of them silently, and `fill()` returns 2 where a caller counting on
`Stack` expects 5. That loss is the right behavior for a ring buffer of
recent events and the wrong behavior for a queue of work that must keep
every item. If `Stack`'s contract includes "every pushed item stays,"
this version still breaks it.

Should `BoundedStack` be a subclass of `Stack`? Probably not. The
exercise has two answers to the same bind:
either weaken the guarantee until it fits the base contract, or admit
that "a stack that can refuse" is a different type. A separate class
states that difference, with its own `push()` returning `bool` or
raising an exception. Nothing then hands that class to a `fill()`
written for a different contract. Inheritance is a claim about
substitutability, and `BoundedStack` makes a claim it cannot keep.

</details>
</details>
</details>
