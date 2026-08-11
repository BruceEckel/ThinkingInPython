# Iterators

An *iterator* decouples an algorithm from the container it uses.
Code written against an iterator does not care whether the data came from a list,
a file, a database cursor, or a computation.
It asks only for the next item.

Python builds iterators into the language.
Any object that follows the *iterator protocol* works with `for`,
comprehensions, `sum()`, `sorted()`, unpacking,
and every function that takes an iterable.

## Iteration Comes Built In

Two methods make up the protocol.
An *iterable* has `__iter__()`, which returns an *iterator*.
An iterator has `__next__()`,
which returns the next item or raises `StopIteration`.
An iterator is also iterable: its `__iter__()` returns itself,
so an iterator works anywhere code expects an iterable.
The `for` loop calls these so you almost never call them directly.
Every container uses this protocol,
so a function written against an iterable stays decoupled from the container.

```python
# basic_iteration.py
nums = [1, 2]
it = iter(nums)  # Called by a for loop
print(iter(nums) is iter(nums))
#: False
print(iter(it) is it)  # An iterator returns itself
#: True
print(next(it), next(it))  # What the loop calls per step
#: 1 2
try:
    next(it)
except StopIteration:
    print("StopIteration ends the loop")
#: StopIteration ends the loop
```

A `for` loop makes one `iter()` call,
then calls `next()` until the iterator raises `StopIteration`.
A loop absorbs `StopIteration` as the normal end rather than an error.
The first `is` shows that calling `iter()` on a list creates a new iterator each time.
The second `is` shows that calling `iter()` on an iterator returns that iterator.
The tempting call is `next(nums)`: `next()` accepts only an iterator,
and a list has no `__next__()`, so that call raises a `TypeError` at runtime,
and the checker rejects it before that.

Written out, `for x in nums:` is this loop:

```
it = iter(nums)          # Once, before the loop
while True:
    try:
        x = next(it)     # Once per step
    except StopIteration:
        break
    ...                  # The loop body
```

One legacy path bypasses `__iter__()`.
A class that defines only `__getitem__()` taking integers from zero is still iterable:
`iter()` builds an iterator that indexes it until `IndexError`.
Such a class works with `for` while failing `isinstance(obj, Iterable)` and failing an `Iterable[T]` annotation,
which is the one case where the loop and the checker disagree.
Write `__iter__()` in new code.

## Generators {#generators}

You rarely write `__iter__()`/`__next__()` by hand.
A *generator* writes them.
A function with a `yield` statement returns an iterator that produces each yielded value in turn,
pausing and resuming its own state.
The generators in this chapter travel one way, so `Iterator[T]` annotates them.
That is the short form of a three-part type that also describes what a generator receives and what it returns.
[Generators](45_Generators.md#annotating-a-generator) covers the full form,
which an Effect system needs.

Writing `__iter__()` as a generator makes a class iterable:

```python
# iterators.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

# Generator function
def fibonacci(n: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# __iter__() makes a class iterable. Often a generator:
@dataclass
class Countdown:
    start: int

    def __iter__(self) -> Iterator[int]:
        n = self.start
        while n > 0:
            yield n
            n -= 1

# A function using an iterable is decoupled from its source:
def total(numbers: Iterable[int]) -> int:
    return sum(numbers)

print(list(fibonacci(8)))
#: [0, 1, 1, 2, 3, 5, 8, 13]
print(list(Countdown(5)))
#: [5, 4, 3, 2, 1]
print(total(fibonacci(8)))  # Works on a generator
#: 33
print(total([1, 2, 3, 4]))  # and a list
#: 10
print(total(Countdown(5)))  # and a custom iterable
#: 15
```

`total()` takes an `Iterable` so it works equally well on the generator,
the list, and the custom `Countdown`.

`fibonacci(8)` returns an iterator, which one pass exhausts.
`Countdown(5)` is an iterable whose `__iter__()` builds a fresh generator for every pass,
so you can iterate it repeatedly, as the tests below confirm.

These tests collect each iterator into a list and compare them,
covering the sequences and their empty edge cases,
and check that `total()` works on every source:

```python
# test_iterators.py
import pytest
from iterators import Countdown, fibonacci, total

@pytest.mark.parametrize("n, expected", [
    (8, [0, 1, 1, 2, 3, 5, 8, 13]),
    (0, []),
    (1, [0]),
])
def test_fibonacci_sequence(n: int, expected: list[int]) -> None:
    assert list(fibonacci(n)) == expected

def test_countdown_sequence() -> None:
    assert list(Countdown(5)) == [5, 4, 3, 2, 1]
    assert list(Countdown(0)) == []

def test_countdown_is_reiterable() -> None:
    c = Countdown(3)
    assert list(c) == [3, 2, 1]
    assert list(c) == [3, 2, 1]  # __iter__ yields a fresh generator

def test_total_over_any_iterable() -> None:
    assert total([1, 2, 3, 4]) == 10
    assert total(fibonacci(8)) == 33
    assert total(Countdown(5)) == 15
```

Generators are lazy.
`fibonacci(1_000_000)` computes nothing until you iterate,
and produces one value at a time,
so it works on streams too large to hold in memory.

A generator can be *infinite*.
A `while True` loop that yields forever, or `itertools.count()`,
produces values on demand with no end.
You take only as many as you need (see `itertools.islice()` below),
which a list cannot do.

## The Costs of Laziness

Laziness has two surprising consequences, and both are silent:

```python
# generator_lifecycle.py
from collections.abc import Iterator

def squares(n: int) -> Iterator[int]:
    print("first next() reached the body")
    for i in range(n):
        yield i * i

sq = squares(6)  # Body not executed
print("created")
#: created
print(next(sq))
#: first next() reached the body
#: 0
print(list(sq))  # The values that are left
#: [1, 4, 9, 16, 25]
print(list(sq))  # Exhausted: empty, and no error
#: []
```

Calling `squares(6)` runs none of its body.
The `print` at the top fires only when something demands the first value.
It fires once, not on every value.
Each later `next()` resumes the body just after the `yield` instead of restarting it.
Any validation at the top of a generator inherits this delay:
a `raise` meant to reject a bad argument fires at first use,
far from the call that caused the problem.

To validate eagerly,
check the arguments in a plain function and have it return an inner generator:

```python
# eager_validation.py
from collections.abc import Iterator

def squares(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError(f"n must not be negative: {n}")
    def produce() -> Iterator[int]:
        for i in range(n):
            yield i * i
    return produce()

try:
    squares(-1)  # Raises now, not at first next()
except ValueError as e:
    print(e)
#: n must not be negative: -1
```

`squares()` has no `yield`, so calling it runs the check immediately.
Only `produce()` waits.

The second surprise is the second call to `list(sq)`.
An exhausted generator does not fail.
It produces nothing,
so the empty `list(sq)` gives you no error to point at the bug.

When you must walk data twice, collect it into a list once,
or hand out an iterable like `Countdown` above,
whose `__iter__()` builds a fresh generator for every pass.

Laziness and single use are separate properties.
`Countdown` is as lazy as the generator its `__iter__()` builds,
yet it survives repeated passes, because each pass gets a fresh iterator.
`range()` works the same way: one `range` object can drive loop after loop.
What runs out is the iterator, not the iterable that made it.

The annotation cannot warn you.
`Iterable[T]` describes a list and a half-spent generator equally well,
so a function that walks its argument twice type-checks and then returns a wrong answer on the second pass:

```python
# walked_twice.py
from collections.abc import Collection, Iterable, Iterator

def gen(n: int) -> Iterator[int]:
    yield from range(n)

def twice_iterable(xs: Iterable[int]) -> tuple[int, int]:
    return sum(xs), sum(xs)

def twice_collection(xs: Collection[int]) -> tuple[int, int]:
    return sum(xs), sum(xs)

print(twice_iterable(gen(3)))  # The checker sees nothing wrong
#: (3, 0)
print(twice_collection([0, 1, 2]))  # The same values, in a list
#: (3, 3)
```

When a function iterates more than once, say so in the signature.
`Collection[T]` and `Sequence[T]` ask for more than iteration,
and no iterator supplies it,
so the checker rejects the generator at the call instead of letting it run wrong.
`twice_collection(gen(3))` is the call `ty` refuses,
which is why the listing cannot show it: a chapter listing must type-check.
`total()` above stays `Iterable[int]` because it sums once.

`itertools.tee(it, 2)` splits one iterator into two independent ones,
which looks like a third option but is rarely cheaper.
The `squares()` below is the plain-function form from `eager_validation.py`,
with the generator expression standing in for `produce()`:

```python
# tee.py
import tracemalloc
from collections.abc import Iterator
from itertools import tee
from typing import Final
from benchmark import report

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

a, b = tee(squares(5))  # Two independent readers, one source
print(list(a), list(b))
#: [0, 1, 4, 9, 16] [0, 1, 4, 9, 16]

N: Final[int] = 100_000
first, second = tee(squares(N))
tracemalloc.start()
for _ in first:  # Drain one branch; second has not started
    pass
buffered, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
collected = list(squares(N))
listed, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()
report(tee_bytes=buffered, list_bytes=listed)
print(f"tee held as much as the list: {buffered > listed * 0.9}")
#: tee held as much as the list: True
```

Both branches see all five squares,
so `tee` delivers the second pass the generator could not.
The second half prices it.
`tee` buffers every item the leading branch consumes until the trailing one catches up,
and draining `first` while `second` waits buffers the whole stream.
That is the memory a list would use, which the comparison confirms
(one machine measured 4,096,544 bytes buffered against 3,999,992 for the list).
Use `tee` when two consumers advance together,
not when one finishes before the other starts.

`tee` is also single-threaded.
Its branches share one buffer with no lock,
so handing them to separate threads corrupts it.
[Concurrency](19_Concurrency.md#sharing-an-iterator-between-threads)
covers `threading.concurrent_tee()`, the thread-safe version,
along with what goes wrong when two threads call `next()` on the same iterator.

## Delegating with `yield from`

A generator can delegate part of its work to another iterator using `yield from`.
This yields every value that iterator produces, in turn,
as if the outer generator had written the loop itself:

```python
# yield_from.py
from collections.abc import Iterator, Sequence

type Nested = int | Sequence[Nested]

def flatten_loop(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            for x in flatten_loop(item):  # Spelled out  # noqa: UP028
                yield x

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            yield from flatten(item)  # The same loop, delegated

data: Sequence[Nested] = [1, [2, 3], [4, [5, 6]], 7]
print(list(flatten_loop(data)))
#: [1, 2, 3, 4, 5, 6, 7]
print(list(flatten(data)))
#: [1, 2, 3, 4, 5, 6, 7]
```

Both functions call themselves on each nested sequence,
and both thread the recursive call's values into the outer stream.
`flatten_loop()` does it by hand: start the recursive call,
then re-yield each value it produces.
`flatten()` replaces those two lines with `yield from`,
and the matching output shows the substitution is exact.

`flatten_loop()` carries a `# noqa` because ruff's `UP028` rule reports a `for` loop that only re-yields,
and tells you to write `yield from` instead.

The two forms agree for a generator that only produces values,
as `flatten()` does.
However, the `yield from` expression has a value:
`result = yield from inner()` binds whatever `inner()` returned when it stopped.
The hand-written loop drops that value.
`yield from` also forwards `send()` and `throw()` into the inner generator,
which the loop cannot do.
[Generators](45_Generators.md#yield-from-composes-descriptions)
works all three channels.

This tests both a nested list and a flat one:

```python
# test_yield_from.py
from collections.abc import Callable, Iterator, Sequence
import pytest
from yield_from import Nested, flatten, flatten_loop

type Flattener = Callable[[Sequence[Nested]], Iterator[int]]

@pytest.mark.parametrize("flatten_with", [flatten, flatten_loop])
@pytest.mark.parametrize("nested, expected", [
    ([1, [2, 3], [4, [5, 6]], 7], [1, 2, 3, 4, 5, 6, 7]),
    ([1, 2, 3], [1, 2, 3]),
])
def test_flatten(
    flatten_with: Flattener,
    nested: Sequence[Nested], expected: list[int]
) -> None:
    assert list(flatten_with(nested)) == expected
```

## Reusable Algorithms

The standard library's `itertools` module contains the generic iterator algorithms `chain()`,
`islice()`, `groupby()`, `takewhile()`, and more.
Each of these consumes and produces iterators.
Combine them with [generator expressions](16_Comprehensions.md#generator-expressions)
such as `(x * x for x in data if x > 0)` to build pipelines that stay lazy end to end.
Each stage pulls one item at a time,
so an infinite source is fine as long as something downstream stops it:

```python
# reusable_algorithms.py
from itertools import count, islice, takewhile

numbers = count(1)  # Infinite: 1, 2, 3, ...
# The generator expression squares the odd numbers, lazily:
odd_squares = (n * n for n in numbers if n % 2)
print(list(islice(odd_squares, 5)))  # Take the first five
#: [1, 9, 25, 49, 81]

# takewhile() stops when its condition fails:
print(list(takewhile(lambda s: s < 50, (n * n for n in count(1)))))
#: [1, 4, 9, 16, 25, 36, 49]
```

Nothing runs until `list()` pulls the values.
`islice()` and `takewhile()` decide when to stop.
The infinite `count(1)` never runs away.
`islice()` is also how you slice an iterator.
A generator defines no `__getitem__()`,
so the list habit `odd_squares[:5]` raises `TypeError` instead.

Choose `takewhile()` deliberately,
because its lookalike is the `if` clause of a generator expression
(or `filter()`), and these behave differently with an infinite source.
The `if` version skips nonmatching values but keeps looking forever,
so once values stop matching, a `list()` around it never returns.
`takewhile()` stops at the first failure.
Skipping and stopping look the same on finite data and behave nothing alike on infinite data.

A test can demonstrate that difference, but not by writing `list(count(1))`.
That call never returns, and the test never finishes.
In the following, `counter()` stands in for `count(1)`.
It counts up the same way,
then raises an exception once something has pulled `LIMIT` values:

```python
# test_endless.py
from collections.abc import Iterator
from itertools import count, islice, takewhile
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

def test_list_of_an_endless_source_never_returns() -> None:
    with pytest.raises(Tripwire):
        list(counter(LIMIT))

def test_the_if_clause_skips_but_never_stops() -> None:
    small = (n for n in counter(LIMIT) if n < 3)
    with pytest.raises(Tripwire):
        list(small)

def test_takewhile_stops_at_the_first_failure() -> None:
    assert list(takewhile(lambda n: n < 3, counter(LIMIT))) == [1, 2]

def test_islice_stops_after_its_count() -> None:
    assert list(islice(counter(LIMIT), 3)) == [1, 2, 3]
```

The first test is `list(count(1))` with a stopping point built into the source.
`list()` asks for value after value and never stops,
so the tripwire fires and no list ever comes back.
The second test is that lookalike.
Nothing after `2` satisfies `n < 3`,
yet `list()` keeps pulling in the hope of another match,
and trips the same wire.
The last two stop on their own and never reach the tripwire.

Failing at 1,000 values stands in for how a real program fails:
it stops responding, or it dies when it exhausts memory.
No tool warns you first.
`ty` accepts `list(count(1))`,
and so does `ruff` with every one of its rules enabled.
Whether an iterator ever ends is not something a checker can decide by reading the code,
and a generator built from `while True` is indistinguishable from a finite one until it runs.
The one rule that touches this code is a comprehension check.
It offers to rewrite `[n for n in count(1)]` as `list(count(1))`,
the same problem with fewer characters.
Nothing in the toolchain discovers problems like this.

## A Type-Checking Iterator

The [Decorator Pattern](14_Decorators.md#the-decorator-pattern)
wraps an existing iterator,
producing a new one with the same interface and added behavior.
Here, you force every item to match an expected type:

```python
# typed_iterator.py
from collections.abc import Iterator
from dataclasses import dataclass
from typing import override

@dataclass(eq=False)
class TypedIterator[T](Iterator[T]):
    imp: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        obj = next(self.imp)
        if not isinstance(obj, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(obj).__name__}")
        return obj
```

Subclassing `collections.abc.Iterator` provides `__iter__()` automatically,
so you need only supply `__next__()`.

The `dataclass` decoration carries `eq=False`.
A data class that generates `__eq__()` sets `__hash__` to `None`,
so the wrapper can no longer go in a set or serve as a dict key,
which every other iterator in Python can do.
Field-by-field comparison is also the wrong question to ask about a cursor:
two wrappers sharing one source compare equal even though they have consumed different numbers of items,
and two wrappers over separate iterators of the same list compare unequal.
Turning equality off restores the identity comparison an iterator should have.

A generator wraps an iterator just as well, and in fewer lines:

```python
# typed_generator.py
from collections.abc import Iterable, Iterator

def typed[T](it: Iterable[object], expected: type[T]) -> Iterator[T]:
    for obj in it:
        if not isinstance(obj, expected):
            raise TypeError(
                f"expected {expected}, got {type(obj).__name__}")
        yield obj

if __name__ == "__main__":
    print(list(typed([1, 2, 3], int)))
#: [1, 2, 3]
```

Use the class when the wrapper needs its own state or extra methods.
Use the generator when it does not.
Either way, the result plugs into every place that accepts an iterator,
because they all use the same protocol.
Their inputs differ, though.
`typed()` takes an `Iterable[object]`, so a list is fine.
`TypedIterator` calls `next()` on what it stores,
so it needs an `Iterator[object]`: write `TypedIterator(iter(items), int)`,
not `TypedIterator(items, int)`.
The checker rejects the second form.
Both take `expected: type[T]`, so the checker carries the element type through.
This way, `typed(items, int)` is an `Iterator[int]`, not an `Iterator[Any]`.

```python
# test_typed.py
import pytest
from typed_generator import typed
from typed_iterator import TypedIterator

def test_typed_generator_passes_and_rejects() -> None:
    assert list(typed([1, 2, 3], int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(typed([1, "two", 3], int))

def test_typed_iterator_passes_and_rejects() -> None:
    assert list(TypedIterator(iter([1, 2, 3]), int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(TypedIterator(iter([1, "two"]), int))
```

## The Pattern That Disappeared

*GoF Design Patterns* gives Iterator a class of its own,
with separate methods to start a traversal, advance it,
test whether it has finished, and read the current item.
Nothing in this chapter looks like that.
Those four methods became two: `__iter__()` and `__next__()`.
The language calls both on your behalf.
[The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves)
describes this dissolution.

Writing the four GoF Iterator methods in Python shows what `first()` and `current_item()` were doing.
Over a list they are unremarkable.
`first()` resets an index, `is_done()` compares it to `len()`,
and `current_item()` reads without consuming.
Over a generator, you can still write all four,
but only by keeping everything the traversal has seen:

```python
# gof_iterator.py
from collections.abc import Iterable, Iterator
from typing import Protocol

DONE = sentinel("DONE")

class GoFIterator[T](Protocol):
    def first(self) -> None: ...
    def advance(self) -> None: ...
    def is_done(self) -> bool: ...
    def current_item(self) -> T: ...

class OverStream[T]:
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        self.seen: list[T] = []  # Every item the traversal has read
        self.index = 0

    def first(self) -> None:
        self.index = 0  # Rewinds into seen, not into source

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

stream = OverStream(x * 2 for x in [1, 2, 3])
print(traverse(stream))
#: [2, 4, 6]
stream.first()
print(traverse(stream))  # A second pass, from a spent generator
#: [2, 4, 6]
print(stream.seen)
#: [2, 4, 6]
```

`traverse()` is the loop a GoF caller writes,
and it drives any type with those four methods,
because `GoFIterator` is a [protocol](20_Rethinking_Objects.md#protocols)
rather than a base class.
The first pass spent the generator,
yet `first()` rewinds and `traverse()` produces the same three values.

`seen` is how.
`is_done()` pulls from the source only when the cache cannot reach the current index,
so every item read once stays read.
`current_item()` then indexes the cache instead of touching the source,
which lets it report a value without advancing.
Look at the last line of output.
By the time all four methods work, `seen` holds the entire stream.
The interface needed more than a buffer: it rebuilt the list.

That is the cost the pattern hides.
`first()` and `current_item()` assume a collection you can re-read and inspect in place,
so honoring them over a stream means recreating one, item by item.
The chapter has now reached that conclusion three times: here,
in `tee`'s buffering,
and in the advice to collect into a list when you must walk data twice.
Python dropped both methods rather than paying for them everywhere.
If you take them away, `advance()` must return the value it reached,
which is `__next__()`.

You can ask a GoF iterator repeatedly whether it has finished,
without disturbing it.
Python makes that question part of `__next__()`,
so the only way to ask is to take.
The answer arrives as a `StopIteration` exception that the `for` loop swallows on your behalf.
You can catch that exception yourself,
or hand `next()` a default and compare against it,
but neither restores the free query of the GoF Iterator:

```python
# asking_costs.py
from collections.abc import Iterator

DONE = sentinel("DONE")

def doubled(source: Iterator[int]) -> Iterator[int]:
    # The exception escapes when the source runs out:
    while True:
        yield next(source) * 2

def doubled_ok(source: Iterator[int]) -> Iterator[int]:
    for n in source:  # The loop absorbs the exception
        yield n * 2

numbers = iter([1, 2])
print(next(numbers, DONE) is DONE)  # Asking consumes the 1
#: False
print(next(numbers, DONE) is DONE)  # Asking consumes the 2
#: False
print(next(numbers, DONE) is DONE)  # No more left
#: True

try:
    print(list(doubled(iter([1, 2]))))
except RuntimeError as e:
    print(f"{type(e).__name__}: {e}")
#: RuntimeError: generator raised StopIteration
print(list(doubled_ok(iter([1, 2]))))
#: [2, 4]
```

Each question costs an item.
Nothing in the protocol looks ahead without advancing,
which is why a peekable iterator must buffer,
and why `tee` buffered a whole stream earlier in this chapter.
`DONE` is a [sentinel](05_Functions.md#default-and-keyword-arguments),
because the answer must differ from every value the source could yield.
`None` collapses an exhausted source and a source that yields `None` into the same reply.
The builtin `iter()` uses a sentinel the same way in its two-argument form:
`iter(callable, DONE)` calls `callable` until it hands back `DONE`.
`doubled()` shows the other half of the price.
Letting `StopIteration` escape a generator body does not end that generator politely.
Since [PEP 479](https://peps.python.org/pep-0479/) it becomes a `RuntimeError`,
turning an ordinary end of stream into a failure that reads like a bug elsewhere.

Only a bare `next()` hands you that exception.
With a default it returns the default,
and every other construct here absorbs it.
`yield from source` ends its delegation when the source runs out,
which covers forwarding values untouched.
It cannot do per-item work, because it passes each value through unchanged.
That is why `doubled_ok()` uses a `for` loop,
which absorbs the exception as every loop in this chapter has.
The fix is almost never a `try`.
Let the loop do the asking.

## The Protocol Answers Nothing for Free

Both surprises in [The Costs of Laziness](#the-costs-of-laziness)
come from the same rule.
The only way to find out whether the body accepts its arguments is to pull a value and let it run,
and the only way to find out whether the source has run out is to pull and get nothing back.
`for` and `list()` catch that second answer and report nothing,
so an exhausted source and an empty one produce identical output.
The protocol costs you nothing, and tells you nothing.

## Exercises

1.  Write a generator `evens(n)` that yields the first `n` even numbers,
    and confirm `total()` from `iterators.py` sums them without modification.
2.  Rewrite `Countdown` to also support `len()`,
    then explain why a generator cannot.
3.  Use `itertools.islice()` to take the first 10 values of `fibonacci(1_000_000)` without computing the rest.
4.  `generator_lifecycle.py` returns an empty list on its second pass.
    Fix the caller two ways: collect into a list once and reuse it,
    then instead convert `squares` into a `Countdown`-style iterable class whose `__iter__()` builds a fresh generator.
    Which fix would you choose for a stream of a million items, and why?
5.  In `tee.py`, consume both branches in lockstep instead of draining one first,
    by looping over `zip(first, second, strict=True)`.
    Predict what happens to `buffered` before you measure it,
    then explain the result using the rule that closes that section.
6.  The prose pairs the generator expression's `if` clause with `filter()`,
    but no test covers `filter()`.
    Add one to `test_endless.py`,
    and say which existing test it should resemble.
7.  `gof_iterator.py` shows only the stream version.
    Write `OverSequence` over a `Sequence[T]`,
    confirm `traverse()` drives it with no changes to `traverse()`,
    and explain why it needs no `seen` list.
    Then build an `OverStream` over `itertools.count(1)`.
    `traverse()` never returns on an endless source,
    so drive the four methods yourself for 50,000 steps and report `len(stream.seen)`.
    What has `first()` cost you on an endless source?
8.  Write `peek(it)` that reports an iterator's next value without consuming it.
    You cannot, so write a `Peekable` wrapper that can,
    and name what it stores that a bare iterator does not.
9.  `flatten()` recurses on anything that is not an `int`.
    Call it on `[1, "ab", 2]` and explain the `RecursionError` you get,
    given that a one-character string is still a `Sequence`.
    Then fix `flatten()` so a `str` yields as one item,
    and say what the same fix would look like in `flatten_loop()`.
10. `typed()` raises a `TypeError` on the first item of the wrong type,
    which ends the stream.
    Write `typed_skipping()`, which drops mismatched items and keeps going,
    then say which of the two you would want wrapping a parsed log file,
    and why.
    Which one is easier to write as `TypedIterator`?
