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

`Countdown` supports `len()` because it is a reusable *iterable*,
not the iterator itself: each `for` loop or `list()` call gets a fresh
generator from a fresh call to `__iter__()`, so `c.start` is
untouched by iterating and `len(c)` can compute directly from it,
any number of times, before or after.

A plain generator cannot do this. Once you call a generator function,
you have the iterator itself, and an iterator's whole state is "how
far through have I gotten," which is exactly what makes counting its
remaining items expensive: the only way to know how many values are
left is to consume them, which uses them up. No `start` field
remains to inspect, and nothing can ask a paused generator "how many
more times will you yield?" without running it to exhaustion. `Countdown`
sidesteps this because it is a container that *produces* a generator
on demand. The container itself keeps the value a `len()` can read
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
so only the first ten iterations of `fibonacci()`'s loop ever run. The
other 999,990 are never computed, the same laziness
[Comprehensions](../Chapters/16_Techniques--Comprehensions.md#generator-expressions) and
[Performance](../Chapters/18_Techniques--Performance.md) both rely on.

## 4. Two fixes for a spent generator

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

Both survive a second pass, and they pay differently. The list holds
every value for as long as the name lives, so a million items is a
million items in memory, and the second pass costs nothing. `Squares`
holds only `n`, and each pass recomputes from scratch.

For a stream of a million items, choose `Squares`. Memory is the
resource that fails catastrophically, as
[Performance](../Chapters/18_Techniques--Performance.md#lazy-evaluation-with-generators)
describes: a data set that fits runs at full speed and one that does
not falls off a cliff into swapping or a `MemoryError`. Recomputation
merely costs time, in proportion. The list wins only when a pass is
expensive and the data is known to be small, or when the source cannot
be replayed at all, as with a network response.

## 5. `tee` consumed in lockstep

```python
# exercise_5.py
import sys
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

if "--numbers" in sys.argv:  # Exact sizes on your machine
    print(f"lockstep {lockstep:,}, drained {drained:,}")
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
            raise Tripwire(
                f"pulled {limit} values and kept asking")
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
anything, which the *GoF* interface assumes a collection can
do. `OverStream` builds `seen` to fake that ability.

The endless source shows what the faking costs. After 50,000 steps
`seen` holds 50,000 items, and it holds a million after a million.
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

## 9. A string that never bottoms out

```python
# exercise_9.py
from collections.abc import Iterator, Sequence

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
try:
    list(flatten(mixed))
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
print(list(flatten_str(mixed)))
#: [1, 'ab', 2]
print(list(flatten_str([1, ["ab", [2]], 3])))
#: [1, 'ab', 2, 3]
```

`flatten()` asks one question, "is this an `int`?", and treats every
other answer as something to recurse into. A `str` is not an `int`, so
`"ab"` goes to `flatten("ab")`, which iterates it into `"a"`. That is
also not an `int`, so it recurses into `flatten("a")`, which iterates
`"a"` into `"a"`. The string has stopped getting shorter. Every other
sequence bottoms out because indexing it eventually yields a non-
sequence, and `str` is the one built-in that never does: a
one-character string is still a `Sequence` of one-character strings.
The recursion has no base case, so it runs until the stack is gone.

The fix widens the base case rather than the recursive one. Testing
`isinstance(item, int | str)` makes `str` a leaf, so it is yielded
whole and never iterated. The return type widens to
`Iterator[int | str]` to say so.

`flatten_loop()` takes the identical fix, since the two differ only in
how they re-yield: `if isinstance(item, int | str)` in the same place,
and the `for x in flatten_loop(item)` branch left alone. The bug is in
the question each version asks, not in the delegation, which is why
`yield from` neither causes it nor cures it.

Worth noting what did not help: `Nested` says a leaf is an `int`, so
the type already claims `"ab"` cannot be there. `ty` accepts the call
anyway. A recursive alias of this shape is checked loosely enough that
the annotation documents the intent without enforcing it, which is why
the failure arrives as a `RecursionError` at runtime rather than an
error at the call.

## 10. Skipping instead of raising

```python
# exercise_10.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override

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
try:
    print(list(typed(items, int)))
except TypeError as e:
    print(e)
#: expected <class 'int'>, got str
print(list(typed_skipping(items, int)))
#: [1, 3, 4]
print(list(SkippingIterator(iter(items), int)))
#: [1, 3, 4]
```

`typed()` and `typed_skipping()` differ by one word, and the
difference decides what a bad item costs. `typed()` ends the stream:
the `1` before `"two"` is delivered, everything after it is not, and
the caller gets an exception instead of a list. `typed_skipping()`
delivers `[1, 3, 4]` and never mentions `"two"` or the `None`.

For a parsed log file, take the skipping version. A log is an
append-only record written by many processes, so a malformed line is
an expected event rather than a broken contract, and one truncated
line should not cost you the rest of the file. The raising version
gives the caller no way to resume: the generator is spent, so
continuing means parsing the file again and somehow starting past the
line that failed.

That choice has a price, and it is the one this chapter keeps
returning to. Skipping is silent, so a filter that quietly drops every
line cannot be told from a file with nothing to report. If you take
the skipping version, count what it drops and report the count.

The class form is harder to write, and the reason is instructive.
A generator may decline to produce: `typed_skipping()` reaches an item
it does not want and simply does not `yield`, and the `for` loop
continues. `__next__()` has no such option. Every call must return a
value or raise `StopIteration`, so `SkippingIterator` needs its own
loop to keep pulling until a match arrives. The raising version needs
no loop at all, since it acts on the one item it just read. Generators
write the state machine for you, and skipping is where you notice.
