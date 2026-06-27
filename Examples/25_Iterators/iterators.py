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
#: [0, 1, 1, 2, 3, 5, 8, 13]
print(list(Countdown(5)))
#: [5, 4, 3, 2, 1]
print(total(fibonacci(8)))   # Works on a generator
#: 33
print(total([1, 2, 3, 4]))   # and on a list
#: 10
print(total(Countdown(5)))   # and on a custom iterable
#: 15
