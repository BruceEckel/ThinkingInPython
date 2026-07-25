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
That is the memory a list would have used,
which the comparison confirms
(one machine measured 4,096,544 bytes buffered against 3,999,992 for the list).
Reach for `tee` when two consumers advance together,
not when one finishes before the other starts.

These tests collect each iterator into a list and compare,
covering the sequences and their empty edge cases,
confirming a custom iterable can be re-iterated,
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

A generator can delegate part of its work to another iterator with `yield from`.
It yields every value produced by that iterator in turn,
as if the outer generator had written the loop itself:

```python
# yield_from.py
from collections.abc import Iterator, Sequence

type Nested = int | Sequence[Nested]

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            yield from flatten(item)

print(list(flatten([1, [2, 3], [4, [5, 6]], 7])))
#: [1, 2, 3, 4, 5, 6, 7]
```

`flatten()` calls itself on each nested sequence,
and `yield from` threads the recursive call's values into the outer stream.
Without it, you would write `for x in flatten(item): yield x`,
which does the same thing but names the loop explicitly.
`yield from` is that loop, spelled as a single delegation.

The two spellings agree for a generator that only produces values,
as `flatten()` does.
They part ways beyond that.
The `yield from` expression has a value:
`result = yield from inner()` binds whatever `inner()` returned when it stopped,
and the hand-written loop drops that value.
`yield from` also forwards `send()` and `throw()` into the inner generator,
which the loop cannot do at all.

This test checks a nested list and a flat one:

```python
# test_yield_from.py
from collections.abc import Sequence
import pytest
from yield_from import Nested, flatten

@pytest.mark.parametrize("nested, expected", [
    ([1, [2, 3], [4, [5, 6]], 7], [1, 2, 3, 4, 5, 6, 7]),
    ([1, 2, 3], [1, 2, 3]),
])
def test_flatten(
    nested: Sequence[Nested], expected: list[int]
) -> None:
    assert list(flatten(nested)) == expected
```

## Reusable Algorithms

The standard library's `itertools` module contains the generic iterator algorithms `chain()`,
`islice()`, `groupby()`, `takewhile()`, and more,
each consuming and producing iterators.
Combined with generator expressions
([Comprehensions](16_Comprehensions.md#generator-expressions)),
such as `(x * x for x in data if x > 0)`,
you can build pipelines that stay lazy end to end.
This pipeline draws from an infinite source but computes only what the consumer takes.
Each stage pulls one item at a time,
so an infinite source is fine as long as something downstream stops it:

```python
# reusable_algorithms.py
from itertools import count, islice, takewhile

numbers = count(1)  # Infinite: 1, 2, 3, ...
# Square the odd numbers, lazily, then take just the first five:
odd_squares = (n * n for n in numbers if n % 2)
print(list(islice(odd_squares, 5)))
#: [1, 9, 25, 49, 81]

# takewhile() stops as soon as its condition fails:
print(list(takewhile(lambda s: s < 50, (n * n for n in count(1)))))
#: [1, 4, 9, 16, 25, 36, 49]
```

Nothing runs until `list()` pulls values through,
and `islice()` and `takewhile()` decide when to stop,
so the infinite `count(1)` never runs away.

Choose `takewhile()` deliberately,
because its lookalike is the `if` clause of a generator expression
(or `filter()`), and they part ways on an infinite source.
The `if` version *skips* nonmatching values but keeps looking forever,
so once values stop matching for good, a `list()` around it never returns.
`takewhile()` *stops* at the first failure.
Skipping and stopping look alike on finite data and behave nothing alike on infinite data.

## A Type-Checking Iterator

The [Decorator Pattern](14_Decorators.md#the-decorator-pattern)
wraps an existing iterator,
producing a new one with the same interface and added behavior.
Here, we force every item to be of an expected type:

```python
# typed_iterator.py
from collections.abc import Iterator
from typing import override

class TypedIterator[T](Iterator[T]):
    def __init__(self, it: Iterator[object],
                 expected: type[T]) -> None:
        self.imp = it
        self.expected = expected

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
so you supply only `__next__()`.
A generator wraps an iterator just as well and in fewer lines:

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
because they all speak the same protocol.
Both take `expected: type[T]`, so the checker carries the element type through.
`typed(items, int)` is an `Iterator[int]`, not an `Iterator[Any]`.

Both wrappers should pass matching items and raise on a mismatch:

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
Four methods became two, `__iter__()` and `__next__()`,
and the language calls both on your behalf.
This is the dissolving that [The Pattern Concept](21_The_Pattern_Concept.md)
describes, carried far enough that using the pattern stops feeling like a decision.

What the absorption took with it was the explicit question.
A GoF iterator is asked whether it is done,
and the code doing the asking can act on the answer.
Python moved that question inside the `for` loop,
which is why both surprises in this chapter are quiet ones.
An exhausted generator reports "finished" to a loop that keeps the news to itself,
and a generator that has not started reports nothing at all.
You get the protocol for free and pay for it in visibility.

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
