# Iterators: Solutions

## 1. `evens(n)`, summed by the unmodified `total()`

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

`evens()` is a generator function which is the same shape as
`fibonacci()`: a function containing `yield`, so calling it returns an
iterator rather than running the body immediately. `total()` calls
`sum()` on whatever iterable it receives, so it sums `evens(5)`'s
values without needing to know that a new kind of generator now exists
alongside `fibonacci()` and `Countdown`.

## 2. `Countdown` with `__len__()`

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
print(len(c))  # Still works after iterating
#: 5
```

`Countdown` can support `len()` because it is a reusable *iterable*,
not the iterator itself: each `for` loop or `list()` call gets a fresh
generator from a fresh call to `__iter__()`, so `c.start` is
untouched by iterating and `len(c)` can compute directly from it,
any number of times, before or after.

A plain generator cannot do this. Once you call a generator function,
you have the iterator itself, and an iterator's whole state is "how
far through have I gotten," which is exactly what makes counting its
remaining items expensive: the only way to know how many values are
left is to consume them, which uses them up. There is no `start` field
left to inspect, and no way to ask a paused generator "how many more
times will you yield?" without running it to exhaustion. `Countdown`
sidesteps this because it is a container that *produces* a generator
on demand; the container itself keeps the value a `len()` can read
without consuming anything.

## 3. The first ten values of `fibonacci(1_000_000)`

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

`fibonacci(1_000_000)` builds a generator that is prepared to yield a
million values, but building it computes nothing yet, since a
generator's body only runs as far as the next `yield` each time
something asks it for a value. `islice(..., 10)` asks for exactly ten,
so only the first ten iterations of `fibonacci()`'s loop ever run; the
other 999,990 are never computed, the same laziness
[Comprehensions](16_Comprehensions.md#generator-expressions) and
[Performance](18_Performance.md) both rely on.

## 4. Two fixes for a spent generator

```python
# exercise_4.py
from collections.abc import Iterator
from dataclasses import dataclass

def squares(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * i

# Fix one: collect once, then reuse the list.
collected = list(squares(5))
print(collected)
#: [0, 1, 4, 9, 16]
print(collected)
#: [0, 1, 4, 9, 16]

# Fix two: an iterable whose __iter__() builds a fresh generator.
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

Both survive a second pass, and they pay differently. The list holds
every value for as long as the name lives, so a million items is a
million items in memory, and the second pass costs nothing. `Squares`
holds only `n`, and each pass recomputes from scratch.

For a stream of a million items, choose `Squares`. Memory is the
resource that fails catastrophically, as
[Performance](18_Performance.md#lazy-evaluation-with-generators)
describes: a data set that fits runs at full speed and one that does
not falls off a cliff into swapping or a `MemoryError`. Recomputation
merely costs time, in proportion. The list wins only when a pass is
expensive and the data is known to be small, or when the source cannot
be replayed at all, as with a network response.

## 5. `tee` consumed in lockstep

```python
# exercise_5.py
import tracemalloc
from collections.abc import Iterator
from itertools import tee

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

N = 100_000

first, second = tee(squares(N))
tracemalloc.start()
for _ in zip(first, second, strict=True):  # Lockstep
    pass
lockstep, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

ahead, behind = tee(squares(N))
tracemalloc.start()
for _ in ahead:  # One branch first, as tee.py does
    pass
drained, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"lockstep under 1% of draining one: "
      f"{lockstep * 100 < drained}")
#: lockstep under 1% of draining one: True
```

The buffer nearly disappears. One machine measured 2,176 bytes for the
lockstep loop against 4,095,200 for draining a branch, about 1,900 to
one.

`tee` buffers what the leading branch has consumed and the trailing one
has not. Draining `first` completely makes that gap the whole stream.
Advancing both together keeps the gap at one item, so the buffer never
grows. This is the rule the section ends on, measured: `tee` is cheap
when consumers move together and costs a full copy when they do not.
Nothing about the call changes, only how the results are used.

## 6. A test for `filter()`

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
            raise Tripwire(f"pulled {limit} values and kept asking")
        yield n

def test_filter_skips_but_never_stops() -> None:
    with pytest.raises(Tripwire):
        list(filter(lambda n: n < 3, counter(LIMIT)))
```

It should resemble `test_the_if_clause_skips_but_never_stops()`,
because `filter()` and the generator expression's `if` clause are the
same operation written two ways. Both skip what does not match and
both keep asking forever, so both trip the wire. Only `takewhile()`
stops.

Writing this test is how you confirm the pairing the prose asserts. A
reader might reasonably guess that `filter()`, being a function rather
than a clause, gets a chance to decide when to stop. It does not: it
receives values one at a time and can only answer "keep" or "skip"
about the value in front of it, never "stop."

## 7. `OverSequence`, and `first()` on an endless source

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

`traverse()` needs no change, because it was written against the
`GoFIterator` protocol rather than a class. `OverSequence` and
`OverStream` share no base class and never mention the protocol, and
both satisfy it by having the four methods.

`OverSequence` needs no `seen` list because the sequence already is
one. It can be indexed repeatedly, in any order, without consuming
anything, which is what the *GoF* interface assumes a collection can
do. `OverStream` builds `seen` to fake that ability.

The endless source shows what the faking costs. After 50,000 steps
`seen` holds 50,000 items, and it would hold a million after a million.
`first()` is only implementable if every value stays reachable, so on a
source with no end, supporting it means unbounded memory. Python's
`__next__()` has no such requirement, which is why `itertools.count()`
is safe to iterate and impossible to rewind.

## 8. A peekable iterator

```python
# exercise_8.py
from collections.abc import Iterable, Iterator
from typing import override

DONE = sentinel("DONE")

class Peekable[T](Iterator[T]):
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        self.stored: T | DONE = next(self.source, DONE)

    def peek(self) -> T | DONE:
        return self.stored  # Reports without consuming

    @override
    def __next__(self) -> T:
        if self.stored is DONE:
            raise StopIteration
        item = self.stored
        self.stored = next(self.source, DONE)
        return item

it = Peekable(x * 2 for x in [1, 2, 3])
print(it.peek(), it.peek(), it.peek())  # Free, and repeatable
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

A bare `peek(it)` function cannot be written. Reading a value requires
`next()`, `next()` advances, and nothing in the protocol puts a value
back. The information you want does not exist anywhere you can reach
without changing the thing you are asking about.

`Peekable` stores what a bare iterator does not: one item, pulled
early. That is the entire difference, and it buys back the
`current_item()` that *GoF* had and Python dropped. `peek()` is now
free and repeatable, exactly as the three identical `2`s show, because
it reads a field rather than the source.

The cost appears in the constructor. `Peekable` pulls from the source
before any caller asks for a value, so an expensive first item is
computed whether or not it is ever used, and a source that blocks on
its first read blocks at construction. That is the same eagerness
`tee`, `OverStream`, and this chapter's other lookahead all pay: a
question about the future is answered by fetching the future.
