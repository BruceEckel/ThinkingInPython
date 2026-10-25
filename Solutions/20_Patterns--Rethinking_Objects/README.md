# Rethinking Objects: Solutions

## 1. A leaking `tags` list, then plugged

> In `leaky.py`, add a `tags: list[str]` field to `Leaky`,
> exposed through a `@property` the same way `numbers` is,
> and demonstrate the same leak by mutating the list you get back.
> Then plug the leak the way `plugged.py` plugs `numbers` and `bob`.

<details>
<summary>Where to look</summary>

[Encapsulation Leaks](../../Chapters/20_Patterns--Rethinking_Objects.md#encapsulation-leaks)
shows a getter that returns a reference to the real internal list.
Mutate what the `tags` property returns to see the leak.
[Plugging Leaks Is Tedious](../../Chapters/20_Patterns--Rethinking_Objects.md#plugging-leaks-is-tedious)
shows the fix: return a copy, so the caller changes only the copy.

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
    def numbers(self) -> list[int]:
        ...

    @property
    def bob(self) -> Bob:
        ...

    @property
    def tags(self) -> list[str]:
        ...
```

```python
# The shape of exercise_1b.py
from copy import deepcopy
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
    def numbers(self) -> list[int]:
        ...

    @property
    def bob(self) -> Bob:
        ...

    @property
    def tags(self) -> list[str]:
        ...
```

<details>
<summary>Done when</summary>

in your `Leaky` version,
appending `"z"` to what `leaky.tags` returns and printing `leaky.tags` shows `['a', 'b', 'z']` for a `Leaky` built with `["a", "b"]`.
The same steps on your `Plugged` version print `['a', 'b']`.

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
    def numbers(self) -> list[int]:
        return self._numbers

    @property
    def bob(self) -> Bob:
        return self._bob

    @property
    def tags(self) -> list[str]:
        return self._tags

leaky = Leaky([1, 2], ["a", "b"])
leaky.tags.append("z")
print(leaky.tags)
#: ['a', 'b', 'z']
```

**Expose the internal list.**
`tags` leaks for the same reason `numbers` does.
The getter returns a reference to the real internal list,
so appending to what it returns mutates `Leaky`'s own state from outside.

```python
# exercise_1b.py
from copy import deepcopy
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
    def numbers(self) -> list[int]:
        return self._numbers.copy()

    @property
    def bob(self) -> Bob:
        return deepcopy(self._bob)

    @property
    def tags(self) -> list[str]:
        return self._tags.copy()

plugged = Plugged([1, 2], ["a", "b"])
plugged.tags.append("z")
print(plugged.tags)
#: ['a', 'b']
```

**Isolate the internal list.**
The caller mutates a throwaway copy.

Every new mutable field needs its own defensive copy.
That repetition is the tedium that motivates freezing the data.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[The Immutability Solution](../../Chapters/20_Patterns--Rethinking_Objects.md#the-immutability-solution)
shows `frozen=True` on a class with a `list` field.
Consider which of two operations `frozen=True` blocks: rebinding a field,
or changing the object to which the field refers.
The generated `__hash__()` hashes the field values,
so look at what it must hash when one value is mutable.

<details>
<summary>Done when</summary>

`uv run ty check` passes on your file,
printing `immutable` after the assignment shows `bob=Bob(name='Ralph')`,
and `hash(immutable)` raises a `TypeError` whose message is `unhashable type: 'Bob'`.
You can also name who must make immutability go all the way down,
and why no tool does it.

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

**Mutate past the frozen field.**
`frozen=True` on `Immutable` blocks rebinding `immutable.bob`.
The block applies to the field, not to the object to which `bob` refers.
That object is now a mutable `Bob`.
The assignment to `name` sets a field of `Bob`,
so the `__setattr__()` that `frozen=True` generated for `Immutable` never runs.

**Check hashability.**
The `hash()` failure is a second symptom of the same shallowness.
`frozen=True` generates a `__hash__()` that hashes the tuple of field values,
so hashing an `Immutable` hashes its `Bob`.
`Bob` is a mutable data class that compares by value.
On such a class, `@dataclass` sets `__hash__` to `None`.
If a field of a `Bob` changes after that `Bob` goes into a dict,
its hash changes while the dict keeps the old one.
A lookup then searches the wrong slot.
With `Bob.__hash__` set to `None`,
`hash()` raises a `TypeError` when it reaches `Bob`.

Restoring `frozen=True` on `Bob` removes the mutation and the hash failure together.
They are one problem: a frozen wrapper around a mutable value.
`frozen_leaky.py` shows the same two symptoms for a `list` field.

The author of each class must make immutability go all the way down,
one field at a time, because `frozen=True` freezes a single level.
Declare `tuple` rather than `list`, `frozenset` rather than `set`,
`frozendict` rather than `dict`,
and a frozen data class rather than a mutable one for any nested value.
You choose those declarations.
Once you write them,
the type checker rejects code that mutates the values they describe.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[What the Shape Does Not Say](../../Chapters/20_Patterns--Rethinking_Objects.md#what-the-shape-does-not-say)
shows two protocols whose `total()` methods have the same shape.
`NewType` gives each `float` a distinct type,
so the type checker rejects a `Weight` passed where the code declares a `Price`.
For the runtime question,
consider what `Weight(2.5)` returns when the program runs.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
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
        ...

def charge(item: Priced) -> float:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` reports `invalid-argument-type` on `charge(package)`,
ending in ``incompatible return types: `Weight` is not assignable to `Price` ``,
with no other diagnostic in your file.
Running the file still prints `4.5`,
and you can say what `Weight(2.5)` returns at runtime.

<details>
<summary>Solution</summary>

If you change the annotation on `Package.total()` to `Weight` and leave `return self.weight_kg` as it is,
`ty` reports an `invalid-return-type` error on that line.
The type checker expects `Weight` and finds `float`.
A `float` becomes a `Weight` only when `Weight()` marks it as one.
The solution wraps the return value in `Weight(...)`,
a call that returns the same float at runtime.

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

The comment lets the listing pass the book's type check while the call still runs and prints `4.5`.

**Give each meaning its own type.**
The two `NewType` declarations make the two return types distinct,
so the type checker now rejects a weight where `Priced` declares a price.

If someone deletes the annotations, the program behaves as it does now.
It prints `4.5` and charges the customer for a number of kilograms.
`NewType` exists only for the type checker.
`Weight(2.5)` returns its argument, the `float` `2.5`,
so at runtime a weight is an ordinary float.
The distinction is real in the source and absent in the process.
[What the Shape Does Not Say](../../Chapters/20_Patterns--Rethinking_Objects.md#what-the-shape-does-not-say)
describes that split.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Protocols Generalize, Composition Adapts](../../Chapters/20_Patterns--Rethinking_Objects.md#protocols-generalize-composition-adapts)
defines the `Coord` protocol and adapts `Pair`,
a class that names its fields `a` and `b`.
Write `TripleCoord` to hold a `Triple` and expose `x` and `y` as read-only properties that return the fields you choose.
`distance()` needs no change, because it reads those two properties alone.

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
<summary>Done when</summary>

`distance(TripleCoord(Triple(3, 0, 99)), TripleCoord(Triple(0, 4, -1)))` prints `5.0`,
`uv run ty check` passes on your file,
and `distance()` reads the same as it does in `distance_protocol.py`.

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

A 2D distance uses two of `Triple`'s three fields.
`TripleCoord` supplies the `Coord` shape for `Triple`,
the same way `PairCoord` supplies it for `Pair`.
`distance()` stays as it is, because it reads `.x` and `.y` alone.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Pattern Matching on a Union](../../Chapters/20_Patterns--Rethinking_Objects.md#pattern-matching-on-a-union)
shows `area()` matching on each member of a closed union.
Add `Square` to the `type Shape` alias and give `area()` a matching `case` with a class pattern.
The final `case _` calls `assert_never()`, whose parameter has the type `Never`.
Remove your new `case` and read the type the checker reports for the argument of `assert_never()`.

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
<summary>Done when</summary>

`uv run ty check` passes with your `Square` case in place,
and `Square(5.0)` gets an area of `25.0`.
With that case commented out,
the checker reports `type-assertion-failure` at `assert_never(shape)`,
with the inferred type `Square & ~Rectangle & ~Circle`.

<details>
<summary>Solution</summary>

If you end the `match` at the `Square` case,
`ty check` still passes on the full listing,
because the three cases cover the union.
Commenting out the `Square` case then produces an `invalid-return-type` error.
That error reports that `area()` can implicitly return `None`,
and it names no shape.
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

`ty check` passes because every member of the `Shape` union now has a matching `case`.
With the two lines of the `Square` case commented out, `ty` reports:

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

**Check exhaustiveness.**
The inferred type names the missing case.
The first two `case` lines rule out `Rectangle` and `Circle`,
so at `case _` the type of `shape` is a `Square` that is neither of them.
`assert_never()` requires `Never`, the type with no values,
so the checker reports the mismatch.
That report is the exhaustiveness check that a closed union makes possible.
The checker reports a forgotten case before the program runs.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A `NullCache`, following `NullLogger`'s shape

> In `null_logger.py`, write a second null-object style class, `NullCache`,
> whose `get(key)` always returns `None` and whose `set(key, value)` discards the value,
> following the same shape as `NullLogger`.

<details>
<summary>Where to look</summary>

[*Null Object*](../../Chapters/20_Patterns--Rethinking_Objects.md#null-object)
shows `NullLogger` standing in for a real logger with the same methods and neutral behavior.
Declare a `Cache` protocol with `get()` and `set()`,
then write `NullCache` to satisfy it.
`NullCache.get()` reports a miss, and its `set()` discards the value.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from typing import Final, Protocol

class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...

class NullCache:
    def get(self, key: str) -> str | None:
        ...

    def set(self, key: str, value: str) -> None:
        ...

NO_CACHE: Final[NullCache] = NullCache()

def render(key: str, cache: Cache = NO_CACHE) -> str:
    ...
```

<details>
<summary>Done when</summary>

calling `set("a", "apple")` on a `NullCache` and then `get("a")` prints `None`,
and `uv run ty check` passes when you hand a `NullCache` to a function whose parameter is a protocol declaring `get()` and `set()`,
with no `is None` test on that parameter.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from typing import Final, Protocol

class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...

class NullCache:
    def get(self, key: str) -> str | None:
        return None

    def set(self, key: str, value: str) -> None:
        pass

NO_CACHE: Final[NullCache] = NullCache()

def render(key: str, cache: Cache = NO_CACHE) -> str:
    cached = cache.get(key)
    if cached is not None:  # A miss is information
        return cached
    page = f"<p>{key}</p>"
    cache.set(key, page)
    return page

NO_CACHE.set("a", "apple")
print(NO_CACHE.get("a"))
#: None
print(render("home"))
#: <p>home</p>
```

`NullCache` is neutral the same way `NullLogger` is.

The `cache` parameter of `render()` has the type `Cache`, not `Cache | None`.
It defaults to the shared `NO_CACHE`, the way `total()` defaults to `SILENT`,
so `render()` has no `is None` branch on the cache.
The `None` that `get()` returns stays in its return type,
because a miss is information on which the caller acts.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Prefer Composition to Inheritance](../../Chapters/20_Patterns--Rethinking_Objects.md#prefer-composition-to-inheritance)
shows `list.extend()` adding items past the overridden `append()`.
Try `extend()` and `insert()` on the subclass and compare the counts with the contents.
The composed version holds a `list` as a field and exposes only methods you write,
so every mutation made through those methods updates a counter.

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
    _items: list[int] = field(default_factory=list)
    appends: int = 0
    sets: int = 0

    def __len__(self) -> int:
        ...

    def append(self, item: int) -> None:
        ...

    def extend(self, more: list[int]) -> None:
        ...

    def __setitem__(self, index: int, value: int) -> None:
        ...
```

<details>
<summary>Done when</summary>

your inheriting `CountingList` ends with more elements than its `append()` and `__setitem__()` counts explain,
after a call to a `list` method you found that goes past both.
Your composed `CountingBox`, after `append(1)`, `extend([2, 3])`,
and `box[0] = 99`, prints `3 3 1` for its length, appends, and sets.

<details>
<summary>Solution</summary>

If you write `CountingBox.extend()` as `self._items.extend(more)`,
the box prints `3 1 1`.
The held list's own `extend()` adds the two elements, so `appends` stays at 1.
As [Prefer Composition to Inheritance](../../Chapters/20_Patterns--Rethinking_Objects.md#prefer-composition-to-inheritance)
notes, composition still allows the bug and moves it into a class you can read.
The solution's `extend()` calls `append()` for each element,
so `appends` counts every element.

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
    _items: list[int] = field(default_factory=list)
    appends: int = 0
    sets: int = 0

    def __len__(self) -> int:
        return len(self._items)

    def append(self, item: int) -> None:
        self.appends += 1
        self._items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

    def __setitem__(self, index: int, value: int) -> None:
        self.sets += 1
        self._items[index] = value

box = CountingBox()
box.append(1)
box.extend([2, 3])
box[0] = 99
print(len(box), box.appends, box.sets)
#: 3 3 1
```

**Count item assignment too.**
The override of `__setitem__()` leaves its parameters unannotated because `list` overloads that method,
once for an index and once for a slice.
The counter treats both forms alike.

**Find the routes past the overrides.**
`extend()` and `insert()` both add elements through `list`'s own C implementation.
That implementation writes the list's storage,
bypassing the Python-level `append()` and `__setitem__()` you overrode.
Other routes past the counters include `+=` and `*=`.
A future CPython could add another.

**Route every mutation through a counter.**
`CountingBox` holds a list rather than being one,
so every mutation made through `CountingBox` runs a method this class wrote.
Each of those methods updates a counter.

`CountingList` gets `sort()`, `index()`, `__len__()`, slicing,
and everything else `list` offers, and gets the counting wrong.
`CountingBox` gets only the methods you write for it.
A caller who needs `sort()` waits until you write one.
With composition, you decide which `list` methods `CountingBox` offers.
With inheritance, `list` decides.
You discover later which of its methods go past your counters.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[The Liskov Substitution Principle](../../Chapters/20_Patterns--Rethinking_Objects.md#liskov-substitution)
shows `fill()` relying on a base `push()` that always succeeds.
Keep that guarantee.
Have `push()` accept every item and enforce the limit another way,
and add a `full()` method that callers can ask.
Then decide whether you can accept what `BoundedStack` gives up to keep that guarantee,
and whether a subclass is the right relationship.

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
<summary>Done when</summary>

`fill(BoundedStack(), 5)` returns `2` and raises no exception,
`fill(Stack(), 5)` still returns `5`,
a caller can ask your `BoundedStack` whether it is full,
and `uv run ty check` passes.
You can also name the guarantee you gave up and decide whether `BoundedStack` should stay a subclass of `Stack`.

<details>
<summary>Solution</summary>

If you have `push()` return `False` when the stack is full,
`ty` reports an `invalid-method-override` error.
The override's `bool` is not assignable to the `None` that `Stack.push()` returns.
`fill()` discards each returned `bool`, three of them `False`, and returns 2.
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

**Expose the limit as a question.**
Callers who care about the limit ask `full()` before pushing.

**Keep the base guarantee.**
`fill()` assumes a `Stack` whose `push()` always succeeds,
so the fix keeps that guarantee.

You give up the refusal.
The original `BoundedStack` guarantees that it accepts at most two items.
This version guarantees only that it keeps at most two.
`fill()` returns 2 where a caller counting on `Stack` expects 5.
A caller who pushes five items silently loses three of them.
That loss is the right behavior for a ring buffer of recent events and the wrong behavior for a queue of work that must keep every item.
If `Stack`'s contract includes "every pushed item stays,"
this version still breaks it.

Should `BoundedStack` be a subclass of `Stack`?
Probably not.
The exercise allows two answers:
either weaken the guarantee until it fits the base contract,
or admit that "a stack that can refuse" is a different type.
A separate class states that difference,
with its own `push()` returning `bool` or raising an exception.
The type checker then rejects any call that hands that class to a `fill()` written for a different contract.
Inheritance is a claim about substitutability.
For `BoundedStack`, that claim is false.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
