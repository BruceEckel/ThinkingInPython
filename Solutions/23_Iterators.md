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
