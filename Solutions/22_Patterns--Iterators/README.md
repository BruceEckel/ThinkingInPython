# Iterators: Solutions

## 1. `evens(n)`, summed by the unmodified `total()`

> Write a generator `evens(n)` that yields the first `n` even numbers,
> and confirm `total()` from `iterators.py` sums them without modification.

<details>
<summary>Where to look</summary>

[Generators](../../Chapters/22_Patterns--Iterators.md#generators)
shows how a function containing `yield` returns an iterator.
Write `evens()` the same way, then pass its result to `total()`.
Any iterable works there, so `total()` works as written.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from collections.abc import Iterable, Iterator

def total(numbers: Iterable[int]) -> int:
    ...

def evens(n: int) -> Iterator[int]:
    ...
```

<details>
<summary>Done when</summary>

`list(evens(5))` prints `[0, 2, 4, 6, 8]` and `total(evens(5))` prints `20`,
with `total()` copied from `iterators.py` unchanged.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from collections.abc import Iterable, Iterator

def total(numbers: Iterable[int]) -> int:
    return sum(numbers)

def evens(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * 2

print(list(evens(5)))
#: [0, 2, 4, 6, 8]
print(total(evens(5)))
#: 20
```

`evens()` is a generator function with the same shape as `fibonacci()`.
Because `evens()` contains `yield`,
calling it returns an iterator rather than running the body immediately.
`total()` passes the iterable it receives to `sum()`,
so it sums `evens(5)` with no change,
as it sums `fibonacci(8)` and `Countdown(5)` in the chapter.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. `Countdown` with `__len__()`

> Rewrite `Countdown` to also support `len()`,
> then explain why a generator cannot.

<details>
<summary>Where to look</summary>

[Generators](../../Chapters/22_Patterns--Iterators.md#generators)
shows `Countdown` as a class whose `__iter__()` is a generator.
Add a `__len__()` that computes the answer from the `start` field.
For the explanation, consider what a generator keeps between calls to `next()`,
and what `len()` would have to do to learn a count.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Iterator
from record import record

@record
class Countdown:
    start: int

    def __iter__(self) -> Iterator[int]:
        ...

    def __len__(self) -> int:
        ...
```

<details>
<summary>Done when</summary>

`len(c)` prints `5` for `Countdown(5)` both before and after `list(c)`,
and `len(Countdown(-1))` and `list(Countdown(-1))` both finish without a `ValueError`.
You can also say what `len()` would have to do to a generator to learn its count.

<details>
<summary>Solution</summary>

If `__len__()` returns `self.start` alone,
`len(Countdown(-1))` raises a `ValueError`,
since `len()` rejects a negative length.
So does `list(Countdown(-1))`,
because `list()` calls `__len__()` to size its result.
A `for` loop over the same object calls `__iter__()` alone,
so it runs zero times and ends normally.
The solution returns `max(self.start, 0)`,
so a negative `start` gives a length of 0, matching the empty iteration.

```python
# exercise_2.py
from collections.abc import Iterator
from record import record

@record
class Countdown:
    start: int

    def __iter__(self) -> Iterator[int]:
        n = self.start
        while n > 0:
            yield n
            n -= 1

    def __len__(self) -> int:
        return max(self.start, 0)

c = Countdown(5)
print(len(c))
#: 5
print(list(c))
#: [5, 4, 3, 2, 1]
print(len(c))  # Still works after iterating over c
#: 5
```

**Build a fresh generator per pass.**
`Countdown` supports `len()` because it is a reusable iterable, not an iterator.
Each `for` loop or `list()` call gets a fresh generator from a fresh call to `__iter__()`,
so iterating over `c` leaves `c.start` alone.

A generator cannot support `len()`.
Once you call a generator function, you have the iterator,
and an iterator's whole state is "how far through have I gotten."
The generator holds no `start` field to inspect,
so to learn how many values remain, you must consume them.

`Countdown` can count because it is a container that produces a generator on demand.
The container keeps the value `len()` reads,
so `len()` answers from the container alone.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. The first ten values of `fibonacci(1_000_000)`

> Use `itertools.islice()` to take the first 10 values of `fibonacci(1_000_000)` without computing the rest.

<details>
<summary>Where to look</summary>

[What Laziness Hides](../../Chapters/22_Patterns--Iterators.md#what-laziness-hides)
explains that a generator's body waits for the first `next()`.
Wrap the generator in `itertools.islice()` with a stop of 10.
`islice()` stops pulling once it has the number you request,
so the generator's loop runs that many iterations.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Iterator
from itertools import islice

def fibonacci(n: int) -> Iterator[int]:
    ...
```

<details>
<summary>Done when</summary>

your file prints `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]` at once,
and `uv run ty check` passes on it.
Slicing the generator with `[:10]` instead makes the type checker report `not-subscriptable`.

<details>
<summary>Solution</summary>

If you slice the generator the way you would a list,
`fibonacci(1_000_000)[:10]` raises a `TypeError`,
because a generator defines no `__getitem__()`.
The type checker rejects the slice before the program runs,
and `ty` reports it as `not-subscriptable`.
As [Reusable Algorithms](../../Chapters/22_Patterns--Iterators.md#reusable-algorithms)
notes, `islice()` slices an iterator by pulling from it.

```python
# exercise_3.py
from collections.abc import Iterator
from itertools import islice

def fibonacci(n: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print(list(islice(fibonacci(1_000_000), 10)))
#: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

`fibonacci(1_000_000)` builds a generator ready to yield a million values,
but building it leaves the body paused before its first line.
Each time something asks a generator for a value,
its body runs to the next `yield` and pauses there.
`islice(..., 10)` asks for ten,
so `fibonacci()`'s loop runs ten iterations and leaves the other 999,990 uncomputed.
[Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#generator-expressions)
and [Performance](../../Chapters/18_Techniques--Performance.md#lazy-evaluation-with-generators)
both rely on the same laziness.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Two fixes for a spent generator

> `generator_lifecycle.py` returns an empty list on its second pass.
> Fix the caller two ways: collect into a list once and reuse it,
> then instead convert `squares()` into a `Countdown`-style iterable class whose `__iter__()` builds a fresh generator.
> Which fix would you choose for a stream of a million items, and why?

<details>
<summary>Where to look</summary>

[An Exhausted Generator Is Silently Empty](../../Chapters/22_Patterns--Iterators.md#an-exhausted-generator-is-silently-empty)
shows the second pass returning an empty list.
One fix stores the values with `list()` once.
The other turns `squares()` into a class whose `__iter__()` builds a new generator on each call.
Weigh the two by what each keeps in memory and what each recomputes.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from collections.abc import Iterator
from record import record

def squares(n: int) -> Iterator[int]:
    ...

@record
class Squares:
    n: int

    def __iter__(self) -> Iterator[int]:
        ...
```

<details>
<summary>Done when</summary>

each fix prints `[0, 1, 4, 9, 16]` on two passes in a row,
where `generator_lifecycle.py` printed an empty list the second time.
You can also name what each fix keeps in memory for a million items,
and what each one recomputes.

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from collections.abc import Iterator
from record import record

def squares(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * i

# Fix one: collect once, then reuse the list
collected = list(squares(5))
print(collected)
#: [0, 1, 4, 9, 16]
print(collected)
#: [0, 1, 4, 9, 16]

# Fix two: __iter__() builds a fresh generator per pass
@record
class Squares:
    n: int

    def __iter__(self) -> Iterator[int]:
        for i in range(self.n):
            yield i * i

sq = Squares(5)
print(list(sq))
#: [0, 1, 4, 9, 16]
print(list(sq))
#: [0, 1, 4, 9, 16]
```

This `squares()` leaves out the chapter's trace line,
since the exercise is about the second pass.
The list holds every value for as long as the name lives,
so a million items is a million items in memory.
`Squares` holds one integer, `n`.
Each pass recomputes the values from scratch.

For a stream of a million items, choose `Squares`.
As [Performance](../../Chapters/18_Techniques--Performance.md#lazy-evaluation-with-generators)
describes, memory is the resource that fails catastrophically.
A data set that fits runs at full speed.
A data set that outgrows memory forces the operating system to swap pages to disk,
or the process fails with a `MemoryError`.
Recomputation, by contrast, takes longer in proportion to the work.
The list is a better choice only when a pass is slow and you know the data is small,
or when the source delivers its data once, as a network response does.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. `tee` with the branches `k` items apart

> `tee.py` measures two extremes: one branch drained before the other starts,
> and both branches in lockstep.
> Measure what lies between them.
> Advance one branch `k` items ahead of the other,
> then walk both together so the leading branch stays `k` items ahead.
> Predict how the buffer grows with `k` before you measure it,
> then measure it for two values of `k` with `traced()`, as `tee.py` does,
> and explain the result using the rule in [What `tee()` Buffers](../../Chapters/22_Patterns--Iterators.md#what-tee-buffers).

<details>
<summary>Where to look</summary>

[What `tee()` Buffers](../../Chapters/22_Patterns--Iterators.md#what-tee-buffers)
gives the rule for what `tee()` holds.
Use `islice()` to advance one branch `k` items,
then walk both with `zip()` so the gap stays the same.
Measure the peak with `traced()` for two values of `k`,
and compare the growth to the size of the gap.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections.abc import Iterator
from itertools import islice, tee
from typing import Final
from benchmark import report, traced

def squares(n: int) -> Iterator[int]:
    ...

N: Final[int] = 100_000

def peak_at_gap(k: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

your file prints `the wider gap buffers more: True`,
and the two peaks `traced()` reports differ by roughly the change in `k` times a constant bytes per item
(about 41 on one machine).
You can explain that constant with the rule in What `tee()` Buffers.

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from collections.abc import Iterator
from itertools import islice, tee
from typing import Final
from benchmark import report, traced

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

N: Final[int] = 100_000

def peak_at_gap(k: int) -> int:
    ahead, behind = tee(squares(N))
    with traced() as memory:
        for _ in islice(ahead, k):  # Open the gap
            pass
        for _ in zip(ahead, behind, strict=False):
            pass  # Both advance, the gap stays k
    return memory.peak

near = peak_at_gap(100)
far = peak_at_gap(10_000)
report(gap_100=near, gap_10_000=far)
print(f"the wider gap buffers more: {far > near}")
#: the wider gap buffers more: True
```

The buffer grows in proportion to `k`.
`tee()` buffers every item the leading branch consumes until the trailing branch catches up,
so a gap of `k` items is a buffer of `k` items,
whatever the length of the stream.
The two measurements in `tee.py` are this rule at its limits.
Draining one branch first stretches the gap to the whole stream.
Lockstep consumption shrinks it to a single item.

**Compare two gap widths.**
One machine measured about 9,300 bytes at `k` of 100 and about 416,000 at `k` of 10,000.
A gap a hundred times wider takes roughly forty-five times the memory rather than a hundred,
because the smaller figure includes overhead that stays the same at every `k`,
and a short gap uses more bytes per item than a long one.
The difference between the two figures tracks `k`:
about 41 bytes per buffered item.

**Report what holds across machines.**
The script prints a boolean rather than the byte counts,
since the sizes shift between machines and between Python builds while their ordering holds.
Pass `--numbers` to see the figures your machine reports.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A test for `filter()`

> The prose pairs the generator expression's `if` clause with `filter()`,
> but no test covers `filter()`.
> Add one to `test_endless.py`,
> and say which existing test it should resemble.

<details>
<summary>Where to look</summary>

[Reusable Algorithms](../../Chapters/22_Patterns--Iterators.md#reusable-algorithms)
pairs the generator expression's `if` clause with `filter()` and contrasts both with `takewhile()`.
Copy the shape of the existing test for the `if` clause, but call `filter()`.
Feed it an endless source that raises an exception after too many pulls,
and use `pytest.raises()` to confirm the filter keeps asking.

<details>
<summary>Done when</summary>

`uv run pytest` passes your new test,
and replacing `filter()` with `takewhile()` in it makes the test fail with `DID NOT RAISE Tripwire`.
You can name the existing test in `test_endless.py` that fails the same way under that swap.

<details>
<summary>Solution</summary>

The solution repeats `test_endless.py`'s scaffolding in a separate file,
so the file runs on its own.
To add the test to `test_endless.py`, copy the test function alone.

```python
# test_ch22_filter.py
from collections.abc import Iterator
from itertools import count
from typing import Final
import pytest

LIMIT: Final[int] = 1000

class Tripwire(Exception):
    pass

def counter(limit: int) -> Iterator[int]:
    for n in count(1):
        if n > limit:
            raise Tripwire(
                f"pulled {limit} values and kept asking")
        yield n

def test_filter_skips_but_never_stops() -> None:
    with pytest.raises(Tripwire):
        list(filter(lambda n: n < 3, counter(LIMIT)))
```

The test should resemble `test_the_if_clause_skips_but_never_stops()`,
because `filter()` and the generator expression's `if` clause are the same operation written two ways.
Both drop each value the predicate rejects and keep asking,
so both raise `Tripwire`.
`takewhile()`, by contrast, stops at the first value its predicate rejects.

Writing this test confirms the pairing the chapter asserts.
A reader might reasonably guess that `filter()`,
being a function rather than a clause, can stop early.
But `filter()` stops only when its source stops.
Its predicate receives one value at a time and answers "keep" or "skip" for that value,
not "stop."

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. `OverSequence`, and `first()` on an endless source

> `gof_iterator.py` shows only the stream version.
> Write `OverSequence` over a `Sequence[T]`,
> confirm `traverse()` drives it with no changes to `traverse()`,
> and explain why it needs no `seen` list.
> Then build an `OverStream` over `itertools.count(1)`.
> `traverse()` runs forever on an infinite source,
> so drive the four methods yourself for 50,000 steps and report `len(stream.seen)`.
> What has `first()` cost you on an infinite source?

<details>
<summary>Where to look</summary>

[The Pattern That Disappeared](../../Chapters/22_Patterns--Iterators.md#the-pattern-that-disappeared)
and [`first()` and `current_item()` Rebuild the List](../../Chapters/22_Patterns--Iterators.md#first-and-current_item-rebuild-the-list)
show the four-method interface over a stream.
`OverSequence` can index its sequence.
`OverStream` must remember every item it has pulled,
so ask what that list does on an endless source.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import count
from typing import Protocol

DONE = sentinel("DONE")

class GoFIterator[T](Protocol):
    def first(self) -> None: ...
    def advance(self) -> None: ...
    def is_done(self) -> bool: ...
    def current_item(self) -> T: ...

@dataclass
class OverSequence[T]:
    items: Sequence[T]
    index: int = 0

    def first(self) -> None:
        ...

    def advance(self) -> None:
        ...

    def is_done(self) -> bool:
        ...

    def current_item(self) -> T:
        ...

class OverStream[T]:
    def __init__(self, source: Iterable[T]) -> None:
        ...

    def first(self) -> None:
        ...

    def advance(self) -> None:
        ...

    def is_done(self) -> bool:
        ...

    def current_item(self) -> T:
        ...

def traverse(it: GoFIterator[int]) -> list[int]:
    ...
```

<details>
<summary>Done when</summary>

`traverse()` returns `[2, 4, 6]` for an `OverSequence` over `[2, 4, 6]`,
and again after `first()`, with `traverse()` unchanged;
your 50,000-step loop over `OverStream(count(1))` prints `50000` for `len(stream.seen)`.
You can say how that number grows with the step count.

<details>
<summary>Solution</summary>

If you pass the endless `OverStream` to `traverse()`, the call runs forever.
`traverse()` stops only when `is_done()` reports the end.
`count(1)` counts forever.
`seen` gains an item on every step for as long as the call runs.

```python
# exercise_7.py
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import count
from typing import Protocol

DONE = sentinel("DONE")

class GoFIterator[T](Protocol):
    def first(self) -> None: ...
    def advance(self) -> None: ...
    def is_done(self) -> bool: ...
    def current_item(self) -> T: ...

@dataclass
class OverSequence[T]:
    items: Sequence[T]
    index: int = 0

    def first(self) -> None:
        self.index = 0

    def advance(self) -> None:
        self.index += 1

    def is_done(self) -> bool:
        return self.index >= len(self.items)

    def current_item(self) -> T:
        return self.items[self.index]

class OverStream[T]:
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        self.seen: list[T] = []
        self.index = 0

    def first(self) -> None:
        self.index = 0

    def advance(self) -> None:
        self.index += 1

    def is_done(self) -> bool:
        while len(self.seen) <= self.index:
            item = next(self.source, DONE)
            if item is DONE:
                return True
            self.seen.append(item)
        return False

    def current_item(self) -> T:
        return self.seen[self.index]

def traverse(it: GoFIterator[int]) -> list[int]:
    out: list[int] = []
    while not it.is_done():
        out.append(it.current_item())
        it.advance()
    return out

seq = OverSequence([2, 4, 6])
print(traverse(seq))
#: [2, 4, 6]
seq.first()
print(traverse(seq))
#: [2, 4, 6]

endless = OverStream(count(1))
for _ in range(50_000):
    endless.is_done()
    endless.current_item()
    endless.advance()
print(len(endless.seen))
#: 50000
```

**Match by methods, not by base.**
`traverse()` works as written,
because its parameter's type is the `GoFIterator` protocol rather than a class.
`OverSequence` and `OverStream` share no base class,
and neither names the protocol.
Defining the protocol's four methods satisfies it.

**Index a stored sequence.**
`OverSequence` rewinds by setting `index` back to 0,
because its `items` sequence holds every value.
A caller can index that sequence repeatedly, in any order,
and every value stays in place.
The GoF interface assumes every collection allows that kind of access,
so `OverStream` builds `seen` to imitate a stored sequence.

**Measure what rewinding needs.**
The endless source shows the memory that imitation takes.
After 50,000 steps `seen` holds 50,000 items,
and after a million steps it holds a million.
`first()` works only if every value stays reachable,
so supporting it on an endless source takes unbounded memory.
Python's iterator protocol has no `first()`,
so `itertools.count()` holds two numbers,
the next value it returns and the step.
Iterating over `count()` takes constant memory.
Rewinding it is impossible.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. A peekable iterator

> Write `peek(it)` that reports an iterator's next value without consuming it.
> You cannot, so write a `Peekable` wrapper that can,
> and name what it stores that a bare iterator does not.

<details>
<summary>Where to look</summary>

[Asking Consumes an Item](../../Chapters/22_Patterns--Iterators.md#asking-consumes-an-item)
shows that looking at the next value of an iterator advances it.
Wrap the source in a class that pulls one item ahead and keeps it in a field.
`peek()` returns that field, and `__next__()` returns it and then refills it,
using a sentinel for the end.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from collections.abc import Iterable, Iterator
from typing import override

DONE = sentinel("DONE")

class Peekable[T](Iterator[T]):
    def __init__(self, source: Iterable[T]) -> None:
        ...

    def peek(self) -> T | DONE:
        ...

    @override
    def __next__(self) -> T:
        ...
```

<details>
<summary>Done when</summary>

over `(x * 2 for x in [1, 2, 3])`, three calls to `peek()` print `2 2 2`,
the next `next()` still returns `2`, `list()` of the rest gives `[4, 6]`,
and `peek()` then reports the end.
You can name the one piece of state your `Peekable` adds.

<details>
<summary>Solution</summary>

If you write `peek(it)` as `return next(it, DONE)` and call it on the demo's `(x * 2 for x in [1, 2, 3])`,
`peek()` reports the `2` and consumes it.
The following `next(it)` returns `4`.
The type checker accepts that version,
so you find the lost value only by running the program.
`Peekable` keeps the pulled item in a field,
where `peek()` reads it any number of times and `__next__()` still returns it.

```python
# exercise_8.py
from collections.abc import Iterable, Iterator
from typing import override

DONE = sentinel("DONE")

class Peekable[T](Iterator[T]):
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        self._stored: T | DONE = next(self.source, DONE)

    def peek(self) -> T | DONE:
        return self._stored  # Reports without consuming

    @override
    def __next__(self) -> T:
        if self._stored is DONE:
            raise StopIteration
        item = self._stored
        self._stored = next(self.source, DONE)
        return item

it = Peekable(x * 2 for x in [1, 2, 3])
# Free, and repeatable
print(it.peek(), it.peek(), it.peek())
#: 2 2 2
print(next(it))
#: 2
print(it.peek())
#: 4
print(list(it))  # Still an ordinary iterator
#: [4, 6]
print(it.peek() is DONE)
#: True
```

You cannot write a bare `peek(it)` function.
Reading a value requires `next()`, `next()` advances,
and nothing in the protocol puts a value back.
Every path to the next value advances the iterator.

**Buffer one item ahead.**
`Peekable` adds one piece of state to a bare iterator: the next item,
pulled early.
That stored item restores the `current_item()` that GoF had and Python dropped.

**Fill the buffer at construction.**
`Peekable` pulls from the source before any caller asks for a value,
so the constructor computes the first item, however slow,
whether or not anything uses it.
A source that blocks on its first read blocks at construction.
`OverStream` pulls early the same way.
Its `is_done()` reads the next item before `current_item()` asks for it.
Answering a question about the next item means fetching that item.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. A string that never bottoms out

> `flatten()` recurses on anything that is not an `int`.
> Call it on `[1, "ab", 2]` and explain the `RecursionError` you get,
> given that a one-character string is still a `Sequence`.
> Then fix `flatten()` so a `str` yields as one item,
> and say what the same fix looks like in `flatten_loop()`.

<details>
<summary>Where to look</summary>

[Delegating with `yield from`](../../Chapters/22_Patterns--Iterators.md#delegating-with-yield-from)
shows `flatten()` and its base case.
Iterating over a `str` produces more strings,
so the recursion has no base case to stop it.
Test for `str` alongside `int` using `isinstance()` with a union,
and apply the same test in `flatten_loop()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from collections.abc import Iterator, Sequence
from exceptions import expect

type Nested = int | Sequence[Nested]

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    ...

def flatten_str(
    nested: Sequence[Nested]
) -> Iterator[int | str]:
    ...
```

<details>
<summary>Done when</summary>

the original `flatten()` raises a `RecursionError` on `[1, "ab", 2]`,
your fixed version prints `[1, 'ab', 2]`,
and `uv run ty check` passes on your file.
A return type left as `Iterator[int]` draws `invalid-yield`.
You can say which line of `flatten_loop()` changes.

<details>
<summary>Solution</summary>

If you add `str` to the `isinstance()` test but leave the return type as `Iterator[int]`,
the program prints the same lists,
and `ty` reports an `invalid-yield` at `yield item`,
whose type is now `int | str`.
The solution widens the return type with the test,
so the annotation declares every kind of leaf the function yields.

```python
# exercise_9.py
from collections.abc import Iterator, Sequence
from exceptions import expect

type Nested = int | Sequence[Nested]

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            yield from flatten(item)

def flatten_str(
    nested: Sequence[Nested]
) -> Iterator[int | str]:
    for item in nested:
        if isinstance(item, int | str):  # A str is one item
            yield item
        else:
            yield from flatten_str(item)

mixed: Sequence[Nested] = [1, "ab", 2]
expect(RecursionError, list, flatten(mixed))
#: [RecursionError] maximum recursion depth exceeded
print(list(flatten_str(mixed)))
#: [1, 'ab', 2]
print(list(flatten_str([1, ["ab", [2]], 3])))
#: [1, 'ab', 2, 3]
```

**Descend until a leaf.**
`"ab"` is a `str`, so it goes to `flatten("ab")`,
which iterates over it and gets `"a"`.
That `"a"` is a `str` too, so `flatten("ab")` recurses into `flatten("a")`,
which iterates over `"a"` and gets `"a"` again.
From here on the string stays one character long.
The recursion into a nested list ends because each level holds one less level of nesting,
until the items are `int`s.
A `str` keeps descending.
Iterating over a string yields strings,
and a one-character string is a `Sequence` of one-character strings.
The recursion has no base case,
so it runs until Python raises a `RecursionError`.

**Treat a string as a leaf.**
The fix widens the base case rather than the recursive one.

`flatten_loop()` takes the identical fix,
since `flatten()` and `flatten_loop()` differ only in how they re-yield.
The fix is the same `if isinstance(item, int | str)` test in the same place,
and the `for x in flatten_loop(item)` branch stays as it is.
The bug is in the test each version applies, not in the delegation,
so `yield from` and `for x in flatten_loop(item)` fail alike.

`ty` accepts the list that triggers the bug.
`Nested` reads as though a leaf must be an `int`.
`ty` enforces that much and rejects a `float` in the same list.
But `ty` accepts `"ab"`, because a `str` is a `Sequence[str]`,
and each of those strings is again a `Sequence[str]`.
The string satisfies the alias's second arm by the same endless descent that breaks `flatten()`.
Pyright rejects the string.
Under `ty` the failure is a `RecursionError` at runtime rather than an error at the assignment.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. Skipping instead of raising

> `typed()` raises a `TypeError` on the first item of the wrong type,
> which ends the stream.
> Write `typed_skipping()`, which drops mismatched items and keeps going,
> then say which of the two you would want wrapping a parsed log file,
> and why.
> Which one is easier to write as `TypedIterator`?

<details>
<summary>Where to look</summary>

[A Type-Checking Iterator](../../Chapters/22_Patterns--Iterators.md#a-type-checking-iterator)
shows `typed()` and `TypedIterator`.
In a generator, `typed_skipping()` yields each item that matches and moves past the others.
In a class, `__next__()` must return a value or raise `StopIteration`,
so it needs a loop that keeps pulling until an item matches.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override
from exceptions import expect

def typed[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    ...

def typed_skipping[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    ...

@dataclass(eq=False)
class SkippingIterator[T](Iterator[T]):
    source: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        ...
```

<details>
<summary>Done when</summary>

over `[1, "two", 3, None, 4]` with `int`,
`typed()` raises a `TypeError` naming `str`,
while `typed_skipping()` and your class version both give `[1, 3, 4]`.
`uv run ty check` passes;
a class version that can fall off the end of `__next__()` draws `invalid-return-type`.

<details>
<summary>Solution</summary>

If `SkippingIterator.__next__()` reads one item and tests it, with no loop,
a mismatch falls off the end of the method, which returns `None`.
Over the demo's `items`, the class produces `[1, None, 3, None, 4]`.
`ty` reports an `invalid-return-type` on that version,
since the method can implicitly return `None`.
The solution loops until an item matches,
so every call returns a value or raises `StopIteration`.
`SkippingIterator` carries `eq=False` for the reason `TypedIterator` does in the chapter:
an iterator wrapper keeps identity comparison and stays hashable.

```python
# exercise_10.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override
from exceptions import expect

def typed[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for item in items:
        if not isinstance(item, expected):
            raise TypeError(
                f"expected {expected}, "
                f"got {type(item).__name__}")
        yield item

def typed_skipping[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for item in items:
        if isinstance(item, expected):
            yield item

@dataclass(eq=False)
class SkippingIterator[T](Iterator[T]):
    source: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        for item in self.source:  # Pull until one matches
            if isinstance(item, self.expected):
                return item
        raise StopIteration

items: list[object] = [1, "two", 3, None, 4]
expect(TypeError, list, typed(items, int))
#: [TypeError] expected <class 'int'>, got str
print(list(typed_skipping(items, int)))
#: [1, 3, 4]
print(list(SkippingIterator(iter(items), int)))
#: [1, 3, 4]
```

**Skip a mismatch and keep going.**
`typed()` and `typed_skipping()` ask the same `isinstance()` question and differ in what they do with a no. `typed()` raises a `TypeError`,
which ends the stream.
A consumer that iterates item by item receives the `1` and then the exception.
A caller that wraps `typed()` in `list()` gets the exception instead of a list.
`typed_skipping()` delivers `[1, 3, 4]` and drops `"two"` and the `None` silently.

For a parsed log file, take the skipping version.
A log is an append-only record that many processes write,
so a malformed line is a routine event rather than a broken contract.
One truncated line should leave the rest of the file readable.
With the version that raises a `TypeError`, the exception ends the generator,
so the caller resumes by parsing the file again and somehow starting past the line that failed.

Skipping hides what it drops.
A filter that quietly drops every line looks the same as an empty file.
If you take the skipping version, count what it drops and report the count.

**Keep pulling until a match.**
The skipping version is harder to write as a class.
A generator can pass over an item.
A generator pauses inside its `for` loop at each `yield` and resumes there on the next call,
so the loop that skips is the loop that yields.
A class's `__next__()` starts over at the top on every call,
and every call must return a value or raise `StopIteration`,
so `SkippingIterator` needs a loop written into the method to keep pulling until a match arrives.
A `__next__()` that raises a `TypeError` is straight-line code.
It reads one item and either returns that item or raises the exception.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
