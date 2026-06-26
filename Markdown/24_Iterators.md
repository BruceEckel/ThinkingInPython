# Iterators

An *iterator* decouples an algorithm from the container it runs on.
Code written against an iterator does not care whether the data came from a list,
a file, a database cursor, or a computation: it just asks for the next item.
Alexander Stepanov, who designed the C++ STL,
put iterators at the center of generic programming for exactly this reason.

In many languages this is a pattern you assemble by hand,
with an `Iterator` interface and classes that implement it.
In Python it is built into the language.
Any object that follows the *iterator protocol* works with `for`,
comprehensions, `sum()`, `sorted()`, unpacking,
and every function that takes an iterable.
The pattern is the language.

## Iteration Is Built In

Two methods make up the protocol.
An *iterable* has `__iter__()`, which returns an *iterator*.
An iterator has `__next__()`,
which returns the next item or raises `StopIteration`.
The `for` loop calls these for you, so you almost never call them directly.
Because every container speaks this one protocol,
a function written against an iterable is automatically decoupled from the container.

## Generators {#generators}

You rarely need to write `__iter__()`/`__next__()` by hand,
because a *generator* writes them for you.
A function with a `yield` statement returns an iterator that produces each yielded value in turn,
pausing and resuming its own state.
A class becomes iterable by writing `__iter__()` as a generator:

```python
# iterators.py
# Iterators and generators are built into Python.
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

# A generator function is the easy way to produce an iterator:
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
## [0, 1, 1, 2, 3, 5, 8, 13]
print(list(Countdown(5)))
## [5, 4, 3, 2, 1]
print(total(fibonacci(8)))   # Works on a generator
## 33
print(total([1, 2, 3, 4]))   # and on a list
## 10
print(total(Countdown(5)))   # and on a custom iterable
## 15
```

`total()` is the decoupled algorithm Stepanov was after:
it works on the generator, the list,
and the custom `Countdown` without knowing or caring which.
Generators are also lazy.
`fibonacci(1_000_000)` computes nothing until you iterate,
and produces one value at a time,
so it works on streams too large to hold in memory.
A generator can even be *infinite*: a `while True` loop that yields forever,
or `itertools.count()`, produces values on demand with no end.
You take only as many as you need (see `itertools.islice()` below),
which a list could never do.

## Reusable Algorithms

Generic iterator algorithms ship in the standard library's `itertools` module:
`chain()`, `islice()`, `groupby()`, `takewhile()`, and more,
each consuming and producing iterators.
Combined with generator expressions, such as `(x * x for x in data if x > 0)`,
they let you build pipelines that stay lazy end to end.
This is the "say what, not how" style the STL aimed for,
available out of the box.

## A Type-Checking Iterator

Sometimes you want to wrap an existing iterator and change its behavior.
That is the *Decorator* pattern:
produce a new iterator with the same interface but added behavior.
Here is one that enforces that every item is of an expected type,
raising otherwise:

```python
# typed_iterator.py
from collections.abc import Iterator
from typing import Any, override

class TypedIterator(Iterator[Any]):
    def __init__(self, it: Iterator[Any], expected: type) -> None:
        self.imp = it
        self.expected = expected

    @override
    def __next__(self) -> Any:
        obj = next(self.imp)
        if not isinstance(obj, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(obj).__name__}")
        return obj
```

Subclassing `collections.abc.Iterator` provides `__iter__()` automatically,
so only `__next__()` is needed.
A generator wraps an iterator just as well and in fewer lines:

```python
# typed_generator.py
# A generator that type-checks each item as it passes through.
from collections.abc import Iterable, Iterator
from typing import Any

def typed(it: Iterable[Any], expected: type) -> Iterator[Any]:
    for obj in it:
        if not isinstance(obj, expected):
            raise TypeError(
                f"expected {expected}, got {type(obj).__name__}")
        yield obj

if __name__ == "__main__":
    print(list(typed([1, 2, 3], int)))
## [1, 2, 3]
```

Use the class when the wrapper needs its own state or extra methods;
use the generator when it does not.
Either way, the result plugs into every place that accepts an iterator,
because they all speak the same protocol.

## Testing Iterators

Iterators are easy to test by collecting them into a list and comparing.
Worth covering: the generated sequences, the empty edge cases,
that a custom iterable can be iterated more than once,
that a function written against `Iterable` works on every source,
and that the type-checking wrappers raise on a mismatch.

```python
# test_iterators.py
import pytest
from iterators import Countdown, fibonacci, total
from typed_generator import typed
from typed_iterator import TypedIterator

def test_fibonacci_sequence() -> None:
    assert list(fibonacci(8)) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert list(fibonacci(0)) == []
    assert list(fibonacci(1)) == [0]

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

def test_typed_generator_passes_and_rejects() -> None:
    assert list(typed([1, 2, 3], int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(typed([1, "two", 3], int))

def test_typed_iterator_passes_and_rejects() -> None:
    assert list(TypedIterator(iter([1, 2, 3]), int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(TypedIterator(iter([1, "two"]), int))
```

## Exercises

1.  Write a generator `evens(n)` that yields the first `n` even numbers,
    and confirm `total()` from `iterators.py` sums them without modification.
2.  Rewrite `Countdown` to also support `len()`,
    then explain why a plain generator cannot.
3.  Use `itertools.islice()` to take the first 10 values of `fibonacci(1_000_000)` without computing the rest.
