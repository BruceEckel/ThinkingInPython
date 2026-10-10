# Iterators: Solutions

## 1. `evens(n)`, summed by the unmodified `total()`

> Write a generator `evens(n)` that yields the first `n` even numbers,
> and confirm `total()` from `iterators.py` sums them without modification.

<details>
<summary>Where to look</summary>

[Generators](../../Chapters/23_Patterns--Iterators.md#generators) shows how a function containing `yield` returns an iterator.
Write `evens()` the same way, then pass its result to `total()`.
Any iterable works there, so `total()` needs no change.

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

`evens()` is a generator function with the same shape as
`fibonacci()`: a function containing `yield`, so calling it returns an
iterator rather than running the body immediately. `total()` calls
`sum()` on whatever iterable it receives, so `total()` sums
`evens(5)`'s values without needing to know that a new kind of
generator now exists alongside `fibonacci()` and `Countdown`.

</details>
</details>
</details>

## 2. `Countdown` with `__len__()`

> Rewrite `Countdown` to also support `len()`,
> then explain why a generator cannot.

<details>
<summary>Where to look</summary>

[Generators](../../Chapters/23_Patterns--Iterators.md#generators) shows `Countdown` as a class whose `__iter__()` is a generator.
Add a `__len__()` that computes the answer from the `start` field.
For the explanation, consider what a generator keeps between calls to `next()`, and what `len()` would have to do to learn a count.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Iterator
from dataclasses import dataclass

@dataclass
class Countdown:
    start: int

    def __iter__(self) -> Iterator[int]:
        ...

    def __len__(self) -> int:
        ...
```

<details>
<summary>Solution</summary>

If `__len__()` returns `self.start` alone,
`len(Countdown(-1))` raises a `ValueError`, since `len()` rejects a negative length.
So does `list(Countdown(-1))`, because `list()` calls `__len__()` to size its result,
though a `for` loop over the same object runs zero times without complaint.
The solution returns `max(self.start, 0)`, so the length matches the zero values that iteration produces.

```python
# exercise_2.py
from collections.abc import Iterator
from dataclasses import dataclass

@dataclass
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

**Build a fresh generator per pass.** `Countdown` supports `len()` because it is a reusable iterable,
not an iterator. Each `for` loop or `list()` call gets a fresh
generator from a fresh call to `__iter__()`, so iterating over `c`
leaves `c.start` alone.

**Count without consuming.** `len(c)` computes from `c.start`, any
number of times, before or after.

A generator cannot support `len()`. Once you call a generator
function, you have the iterator, and an iterator's whole state
is "how far through have I gotten." That makes counting its
remaining items expensive. The only way to learn how many values
remain is to consume them, which uses them up. No `start` field
remains to inspect, and nothing can ask a paused generator "how many
more times will you yield?" without running it to exhaustion.
`Countdown` escapes that expense because it is a container that
produces a generator on demand. The container keeps the value
`len()` reads, and reading it consumes nothing.

</details>
</details>
</details>

## 3. The first ten values of `fibonacci(1_000_000)`

> Use `itertools.islice()` to take the first 10 values of `fibonacci(1_000_000)` without computing the rest.

<details>
<summary>Where to look</summary>

[The Costs of Laziness](../../Chapters/23_Patterns--Iterators.md#the-costs-of-laziness) explains that creating a generator runs none of its body.
Wrap the generator in `itertools.islice()` with a stop of 10.
`islice()` pulls only as many values as you request, so the rest stay uncomputed.

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
<summary>Solution</summary>

If you slice the generator the way you would a list,
`fibonacci(1_000_000)[:10]` raises a `TypeError`, because a generator defines no `__getitem__()`.
The type checker rejects the slice before the program runs, and `ty` reports it as `not-subscriptable`.
`islice()` slices an iterator by pulling from it,
as [Reusable Algorithms](../../Chapters/23_Patterns--Iterators.md#reusable-algorithms) notes.

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

`fibonacci(1_000_000)` builds a generator ready to yield a million
values, but building it computes nothing. A generator's body runs only
as far as the next `yield`, each time something asks it for a value.
`islice(..., 10)` asks for exactly ten, so `fibonacci()`'s loop runs
ten iterations and leaves the other 999,990 uncomputed, the same
laziness on which
[Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#generator-expressions) and
[Performance](../../Chapters/18_Techniques--Performance.md#lazy-evaluation-with-generators)
both rely.

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

[An Exhausted Generator Is Silently Empty](../../Chapters/23_Patterns--Iterators.md#an-exhausted-generator-is-silently-empty) shows the second pass returning nothing.
One fix stores the values with `list()` once.
The other turns `squares()` into a class
whose `__iter__()` builds a new generator on each call.
Weigh the two by what each keeps in memory and what each recomputes.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from collections.abc import Iterator
from dataclasses import dataclass

def squares(n: int) -> Iterator[int]:
    ...

@dataclass
class Squares:
    n: int

    def __iter__(self) -> Iterator[int]:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from collections.abc import Iterator
from dataclasses import dataclass

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
@dataclass
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

Both fixes survive a second pass, and they pay differently. The list holds
every value for as long as the name lives, so a million items is a
million items in memory, and the second pass costs nothing. `Squares`
holds one integer, `n`, and each pass recomputes from scratch.

For a stream of a million items, choose `Squares`. Memory is the
resource that fails catastrophically, as
[Performance](../../Chapters/18_Techniques--Performance.md#lazy-evaluation-with-generators)
describes. A data set that fits runs at full speed, and one that does
not falls off a cliff into swapping or a `MemoryError`. Recomputation
merely costs time, in proportion. The list wins only when a pass is
expensive and you know the data is small, or when nothing can replay
the source, as with a network response.

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
> then measure it for two values of `k` with `tee.py`'s `tracemalloc` approach,
> and explain the result using the rule in [What `tee()` Buffers](../../Chapters/23_Patterns--Iterators.md#what-tee-buffers).

<details>
<summary>Where to look</summary>

[What `tee()` Buffers](../../Chapters/23_Patterns--Iterators.md#what-tee-buffers) gives the rule for what `tee()` holds.
Use `islice()` to advance one branch `k` items, then walk both with `zip()` so the gap stays the same.
Measure the peak with `tracemalloc` for two values of `k`, and compare the growth to the size of the gap.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
import tracemalloc
from collections.abc import Iterator
from itertools import islice, tee
from typing import Final
from benchmark import report

def squares(n: int) -> Iterator[int]:
    ...

N: Final[int] = 100_000

def peak_at_gap(k: int) -> int:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_5.py
import tracemalloc
from collections.abc import Iterator
from itertools import islice, tee
from typing import Final
from benchmark import report

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

N: Final[int] = 100_000

def peak_at_gap(k: int) -> int:
    ahead, behind = tee(squares(N))
    tracemalloc.start()
    for _ in islice(ahead, k):  # Open the gap
        pass
    for _ in zip(ahead, behind, strict=False):
        pass  # Both advance, the gap stays k
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak

near = peak_at_gap(100)
far = peak_at_gap(10_000)
report(gap_100=near, gap_10_000=far)
print(f"the wider gap buffers more: {far > near}")
#: the wider gap buffers more: True
```

The buffer grows in proportion to `k`. `tee()` holds what the leading
branch has consumed and the trailing one has not, so a gap of `k` items
is a buffer of `k` items, whatever the length of the stream. The two
measurements in `tee.py` are this rule at its limits. Draining one
branch first stretches the gap to the whole stream, and lockstep
consumption shrinks it to a single item.

**Hold the gap at `k` items.** `islice(ahead, k)` opens the gap, and the `zip()` loop holds it there.
Each step takes one item from each branch, so the buffer keeps its
size through the rest of the run.

**Compare two gap widths.** One machine measured about
9,400 bytes at `k` of 100 and about 416,000 at `k` of 10,000. A
hundredfold wider gap costs roughly forty times the memory rather than
a hundred, because the smaller figure carries a cost that stays
the same at every `k`, and a short gap pays more per item than a long one.
The difference between the two figures, about 41 bytes per
buffered item, is the part that tracks `k`.

**Report what holds across machines.** The script prints a boolean rather than the byte counts, since the
sizes shift between machines and Python builds while their ordering
holds. Pass `--numbers` to see the figures your machine reports.

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

[Reusable Algorithms](../../Chapters/23_Patterns--Iterators.md#reusable-algorithms) pairs the generator expression's `if` clause with `filter()` and contrasts both with `takewhile()`.
Copy the shape of the existing test for the `if` clause, but call `filter()`.
Feed it an endless source that raises an exception after too many pulls, and use `pytest.raises()` to confirm the filter keeps asking.

<details>
<summary>Solution</summary>

The solution repeats `test_endless.py`'s scaffolding in a file of its
own, so it runs without the chapter's module. In the chapter, you add
the test function alone.

```python
# test_ch23_filter.py
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

The test should resemble
`test_the_if_clause_skips_but_never_stops()`, because `filter()` and
the generator expression's `if` clause are the same operation written
two ways. Both skip what does not match and both keep asking forever,
so both trip the wire. Only `takewhile()` stops.

Writing this test confirms the pairing the prose asserts. A
reader might reasonably guess that `filter()`, being a function rather
than a clause, gets a chance to decide when to stop. `filter()` gets
no such chance. It receives values one at a time and can answer
"keep" or "skip" about the value in front of it, not "stop."

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

[The Pattern That Disappeared](../../Chapters/23_Patterns--Iterators.md#the-pattern-that-disappeared) and [`first()` and `current_item()` Rebuild the List](../../Chapters/23_Patterns--Iterators.md#first-and-current_item-rebuild-the-list) show the four-method interface over a stream.
`OverSequence` can index its sequence.
`OverStream` must remember every item it has pulled, so ask what that list does on an endless source.

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
<summary>Solution</summary>

If you pass the endless `OverStream` to `traverse()`,
the call runs forever.
`traverse()` stops only when `is_done()` reports the end, and `count(1)` has none.
`seen` gains an item on every step for as long as the call runs.
The solution calls the four methods in a loop of 50,000 steps instead,
so the run ends and the listing prints `len(endless.seen)`.

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

**Match by methods, not by base.** `traverse()` needs no change, because its parameter names the
`GoFIterator` protocol rather than a class. `OverSequence` and
`OverStream` share no base class, and neither names the protocol.
Defining its four methods is enough to satisfy it.

**Read without consuming.** `OverSequence` needs no `seen` list because its `items` sequence
holds every value. A caller can index that sequence
repeatedly, in any order, without consuming it, and the GoF
interface assumes a collection allows that. `OverStream`
builds `seen` to fake the same ability.

**Measure what rewinding costs.** The endless source shows what the faking costs. After 50,000 steps
`seen` holds 50,000 items, and it holds a million after a million.
`first()` works only if every value stays reachable, so supporting it
on an endless source costs unbounded memory. Python's `__next__()` has
no such requirement, which is why iterating over `itertools.count()`
is safe and rewinding it is impossible.

</details>
</details>
</details>

## 8. A peekable iterator

> Write `peek(it)` that reports an iterator's next value without consuming it.
> You cannot, so write a `Peekable` wrapper that can,
> and name what it stores that a bare iterator does not.

<details>
<summary>Where to look</summary>

[Asking Consumes an Item](../../Chapters/23_Patterns--Iterators.md#asking-consumes-an-item) shows that looking at the next value of an iterator advances it.
Wrap the source in a class that pulls one item ahead and keeps it in a field.
`peek()` returns that field, and `__next__()` returns it and then refills it, using a sentinel for the end.

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
<summary>Solution</summary>

If you write `peek(it)` as `return next(it, DONE)`
and call it on the demo's `(x * 2 for x in [1, 2, 3])`,
it reports the `2` and consumes it.
The following `next(it)` returns `4`.
The type checker passes that version, so the loss shows only when the program runs.
`Peekable` keeps the pulled item in a field,
where `peek()` can read it any number of times and `__next__()` can still hand it out.

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

You cannot write a bare `peek(it)` function. Reading a value requires
`next()`, `next()` advances, and nothing in the protocol puts a value
back. Every path to the next value advances the iterator.

**Buffer one item ahead.** `Peekable` stores what a bare iterator does not: one item, pulled
early. That one stored item is the difference, and it restores
the `current_item()` that GoF had and Python dropped. `peek()` is
now free and repeatable, as the three identical `2`s show,
because it reads a field rather than the source.

**Fill the buffer at construction.** The cost appears in the constructor. `Peekable` pulls from the source
before any caller asks for a value, so the constructor computes an
expensive first item whether or not anything uses it. A source that
blocks on its first read blocks at construction. The early pull is the same
eagerness `tee()`, `OverStream`, and this chapter's other lookahead all
pay. Answering a question about the future means fetching the future.

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

[Delegating with `yield from`](../../Chapters/23_Patterns--Iterators.md#delegating-with-yield-from) shows `flatten()` and its base case.
Iterating over a `str` produces more strings, so the recursion has no base case to stop it.
Test for `str` alongside `int` using `isinstance()` with a union, and apply the same test in `flatten_loop()`.

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
<summary>Solution</summary>

If you add `str` to the `isinstance()` test but leave the return type as `Iterator[int]`,
the program prints the same lists,
and `ty` reports an `invalid-yield` at `yield item`, whose type is now `int | str`.
The solution widens the return type with the test, so the annotation names every kind of leaf the function yields.

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

**Descend until a leaf.** `flatten()` asks of each item whether it
is an `int`, and recurses into every item that is not one. A `str` is not
an `int`, so `"ab"` goes to `flatten("ab")`, which iterates over it
and gets `"a"`. That `"a"` is also not an `int`, so `flatten("ab")`
recurses into `flatten("a")`, which iterates over `"a"` and gets
`"a"`. The string has stopped getting shorter. Every other sequence bottoms out because
indexing it eventually yields a non-sequence, and `str` is the one
built-in exception. A one-character string is still a `Sequence`
of one-character strings. The recursion has no base case, so it runs
until Python raises a `RecursionError`.

**Treat a string as a leaf.** The fix widens the base case rather than the recursive one. Testing
`isinstance(item, int | str)` makes `str` a leaf, so `flatten_str()`
yields each string whole instead of iterating over it. The return type
widens to `Iterator[int | str]` to say so.

`flatten_loop()` takes the identical fix, since `flatten()` and
`flatten_loop()` differ only in how they re-yield. The fix is the same
`if isinstance(item, int | str)` test in the same place, with the
`for x in flatten_loop(item)` branch left alone. The bug is in the
question each version asks, not in the delegation, which is why
`yield from` neither causes the bug nor cures it.

The annotation does not help. `Nested` reads as though a leaf must
be an `int`, and `ty` enforces that much. It rejects a `float` in
the same list. It accepts `"ab"`, because a `str` is a
`Sequence[str]`, and each of those strings is again a
`Sequence[str]`. The string satisfies the alias's second arm by the
same endless descent that breaks `flatten()`. Pyright rejects the
string. Under `ty` the failure arrives as a `RecursionError` at
runtime rather than an error at the assignment.

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

[A Type-Checking Iterator](../../Chapters/23_Patterns--Iterators.md#a-type-checking-iterator) shows `typed()` and `TypedIterator`.
In a generator, `typed_skipping()` does not `yield` a mismatched item.
In a class, `__next__()` must return a value or raise `StopIteration`, so it needs a loop that keeps pulling until an item matches.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override
from exceptions import expect

def typed[T](
    it: Iterable[object], expected: type[T]
) -> Iterator[T]:
    ...

def typed_skipping[T](
    it: Iterable[object], expected: type[T]
) -> Iterator[T]:
    ...

@dataclass(eq=False)
class SkippingIterator[T](Iterator[T]):
    imp: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        ...
```

<details>
<summary>Solution</summary>

If `SkippingIterator.__next__()` drops the loop and tests only the one item it reads,
a mismatch falls off the end of the method, which returns `None`.
Over the demo's `items`, the class produces `[1, None, 3, None, 4]`.
`ty` catches that version with an `invalid-return-type`, since the method can implicitly return `None`.
The solution loops until an item matches,
so every call returns a value or raises `StopIteration`.

```python
# exercise_10.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override
from exceptions import expect

def typed[T](
    it: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for obj in it:
        if not isinstance(obj, expected):
            raise TypeError(
                f"expected {expected}, "
                f"got {type(obj).__name__}")
        yield obj

def typed_skipping[T](
    it: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for obj in it:
        if isinstance(obj, expected):
            yield obj

@dataclass(eq=False)
class SkippingIterator[T](Iterator[T]):
    imp: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        for obj in self.imp:  # Pull until one matches
            if isinstance(obj, self.expected):
                return obj
        raise StopIteration

items: list[object] = [1, "two", 3, None, 4]
expect(TypeError, list, typed(items, int))
#: [TypeError] expected <class 'int'>, got str
print(list(typed_skipping(items, int)))
#: [1, 3, 4]
print(list(SkippingIterator(iter(items), int)))
#: [1, 3, 4]
```

**Skip a mismatch and keep going.** `typed()` and `typed_skipping()` ask the same `isinstance()` question
and act differently on a no, and that difference decides what a bad
item costs. `typed()` ends the stream. The consumer receives the `1`
before `"two"` and nothing after it. The caller gets an exception
instead of a list. `typed_skipping()` delivers `[1, 3, 4]` and says
nothing about `"two"` or the `None`.

For a parsed log file, take the skipping version. A log is an
append-only record that many processes write, so a malformed line is
an expected event rather than a broken contract. One truncated line
should not cost you the rest of the file. The version that raises a
`TypeError` gives the caller no way to resume. The exception ends the
generator, so continuing means parsing the file again and somehow
starting past the line that failed.

That choice has a price, and it is the one this chapter keeps
revisiting. Skipping is silent, so a filter that quietly drops every
line looks the same as a file with nothing to report. If you take the
skipping version, count what it drops and report the count.

**Keep pulling until a match.** The skipping version is harder to write as a class.
A generator may decline to produce a value. `typed_skipping()` reaches
an item of the wrong type and does not `yield`, so the `for`
loop continues. `__next__()` has no such option. Every call must
return a value or raise `StopIteration`, so `SkippingIterator` needs
its own loop to keep pulling until a match arrives. A `__next__()`
that raises a `TypeError` needs no loop, since it acts on the one item
it just read. Generators write the state machine for you, and skipping
is where you notice.

</details>
</details>
</details>
