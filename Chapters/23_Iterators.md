# Iterators

An *iterator* decouples an algorithm from the container it uses.
Code written against an iterator does not care whether the data came from a list,
a file, a database cursor, or a computation.
It only asks for the next item.

Python builds iterators into the language.
Any object that follows the *iterator protocol* works with `for`,
comprehensions, `sum()`, `sorted()`, unpacking,
and every function that takes an iterable.

## Iteration Is Built In

Two methods make up the protocol.
An *iterable* has `__iter__()`, which returns an *iterator*.
An iterator has `__next__()`,
which returns the next item or raises `StopIteration`.
An iterator is also iterable: its `__iter__()` returns itself,
so an iterator works anywhere an iterable is expected.
The `for` loop calls these for you, so you almost never call them directly.
Every container uses this protocol,
so a function written against an iterable automatically stays decoupled from the container.

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
then calls `next()` until `StopIteration` occurs.
A loop absorbs `StopIteration` as the normal end rather than an error.
The first `is` shows that calling `iter()` creates a new iterator.
The second `is` shows that an iterator returns itself.

## Generators {#generators}

You rarely write `__iter__()`/`__next__()` by hand.
A *generator* writes them for you.
A function with a `yield` statement returns an iterator that produces each yielded value in turn,
pausing and resuming its own state.
A class becomes iterable by writing `__iter__()` as a generator:

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
so it can be iterated repeatedly, as the re-iteration test below confirms.

Generators are lazy.
`fibonacci(1_000_000)` computes nothing until you iterate,
and produces one value at a time,
so it works on streams too large to hold in memory.

A generator can even be *infinite*.
A `while True` loop that yields forever, or `itertools.count()`,
produces values on demand with no end.
You take only as many as you need (see `itertools.islice()` below),
which a list cannot do.

There are two surprising consequences of laziness.
Both are silent:

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
print(list(sq))  # Remainder of list
#: [1, 4, 9, 16, 25]
print(list(sq))  # Exhausted: empty, and no error
#: []
```

Calling `squares(6)` runs none of its body.
The `print` at the top fires only when the first value is demanded.
Any validation at the top of a generator inherits this delay:
a `raise` meant to reject a bad argument fires at first use,
far from the call that caused the problem.

To validate eagerly,
check the arguments in a plain function and have it return an inner generator.

The second surprise is the second call to `list(sq)`.
An exhausted generator does not fail.
It produces nothing,
so the empty `list(sq)` gives you no error to point at the bug.

When data must be walked twice, collect it into a list once,
or hand out an iterable like `Countdown` above,
whose `__iter__()` builds a fresh generator for every pass.

`itertools.tee(it, 2)` splits one iterator into two independent ones,
which looks like a third option but is rarely cheaper:

```python
# tee.py
import tracemalloc
from collections.abc import Iterator
from itertools import tee

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

a, b = tee(squares(5))  # Two independent readers, one source
print(list(a), list(b))
#: [0, 1, 4, 9, 16] [0, 1, 4, 9, 16]

N = 100_000
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
print(f"tee held as much as the list: {buffered > listed * 0.9}")
#: tee held as much as the list: True
```

Both branches see all five squares,
so `tee` delivers the second pass the generator could not.
The second half prices it.
`tee` buffers every item the leading branch consumes until the trailing one catches up,
and draining `first` while `second` waits buffers the whole stream.
That is the memory a list would have used, which the comparison confirms
(one machine measured 4,096,544 bytes buffered against 3,999,992 for the list).
Use `tee` when two consumers advance together,
not when one finishes before the other starts.

These tests collect each iterator into a list and compare them,
covering the sequences and their empty edge cases.
This confirms that a custom iterable can be re-iterated,
and that `total()` works on every source:

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

## Delegating with `yield from`

A generator can delegate part of its work to another iterator using `yield from`.
This yields every value produced by that iterator in turn,
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

`flatten_loop()` carries a `# noqa` because ruff's `UP028` rule reports a `for` loop that only re-yields and tells you to write `yield from` instead.

The two spellings agree for a generator that only produces values,
as `flatten()` does.
However, the `yield from` expression has a value:
`result = yield from inner()` binds whatever `inner()` returned when it stopped.
The hand-written loop drops that value.
`yield from` also forwards `send()` and `throw()` into the inner generator,
which the loop cannot do.

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
Combined with [generator expressions](16_Comprehensions.md#generator-expressions)
such as `(x * x for x in data if x > 0)`,
you can build pipelines that stay lazy end to end.
Such a pipeline draws from an infinite source but computes only what the consumer takes.
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

Choose `takewhile()` deliberately,
because its lookalike is the `if` clause of a generator expression
(or `filter()`), and these behave differently with an infinite source.
The `if` version *skips* nonmatching values but keeps looking forever,
so once values stop matching, a `list()` around it never returns.
`takewhile()` *stops* at the first failure.
Skipping and stopping look the same on finite data and behave nothing alike on infinite data.

A test can demonstrate that difference, but not by writing `list(count(1))`.
That call never returns, and no test survives.
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

The first test is `list(count(1))` but with a builtin termination.
`list()` asks for value after value and never stops,
so the tripwire fires rather than the list being returned.
The second test is the near-miss described previously.
Nothing after `2` satisfies `n < 3`,
yet `list()` keeps pulling in the hope of another match,
and trips the same wire.
The last two stop on their own and never reach the trip wire.

Failing at 1,000 values is a stand-in for a real program's failure,
which stops responding or dies when it exhausts memory.
No tool warns you first.
`ty` accepts `list(count(1))`,
and so does `ruff` with every one of its rules enabled.
Whether an iterator ever ends is not something a checker can decide by reading the code,
and a generator built from `while True` is indistinguishable from a finite one until it runs.
The one rule that touches this code is a comprehension check that offers to rewrite `[n for n in count(1)]` as `list(count(1))`,
the same problem with fewer characters.
Nothing in the toolchain (except an AI) will discover problems like this.

## A Type-Checking Iterator

The [Decorator Pattern](14_Decorators.md#the-decorator-pattern)
wraps an existing iterator,
producing a new one with the same interface and added behavior.
Here, we force every item to be of an expected type:

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

Note the `eq=False` in the `dataclass` decoration.
A data class that generates `__eq__()` sets `__hash__` to `None`.
Comparing iterators by field value is incorrect because two wrappers over one source would compare equal no matter how far each had advanced.
Turning equality off restores the correct identity comparison for an iterator.

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

*GoF Design Patterns* gives Iterator a pattern of its own,
with separate methods to start a traversal, advance it,
test whether it has finished, and read the current item.
Nothing in this chapter looks like that.
Those four methods became two: `__iter__()` and `__next__()`.
The language calls both on your behalf.
This is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md).

You can ask a GoF iterator whether it is done multiple times without disturbing it.
Python fuses that question into `__next__()`, so the only way to ask is to take.
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
which is why a peekable iterator has to buffer,
and why `tee` buffered a whole stream earlier in this chapter.
`DONE` is a [sentinel](05_Functions.md#default-and-keyword-arguments),
because the answer must be distinguishable from every value the source could yield.
`None` would collapse an exhausted source and a source that yielded `None` into the same reply.
`doubled()` shows the other half of the price.
Letting `StopIteration` escape a generator body does not end that generator politely.
Since [PEP 479](https://peps.python.org/pep-0479/) it becomes a `RuntimeError`,
turning an ordinary end of stream into a failure that reads like a bug elsewhere.

Only `next()` in a loop hands you that exception.
The alternatives absorb it for you.
`yield from source` ends its delegation when the source runs out,
which includes forwarding values untouched.
It cannot do per-item work, because it passes each value through unchanged.
That is why `doubled_ok()` uses a `for` loop,
which absorbs the exception as every loop in this chapter has.
The fix is almost never a `try`.
It is to let the loop do the asking.

Both surprises earlier in this chapter come from the same fusion.
`for` and `list()` catch the answer for you and report nothing,
so an exhausted source and an empty one produce identical output.
The protocol is free, and quiet.

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
