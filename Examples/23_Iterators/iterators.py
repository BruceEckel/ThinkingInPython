# iterators.py
# Iterators and generators are built into Python.
from collections.abc import Iterable, Iterator


# A generator function is the easy way to produce an iterator:
def fibonacci(n: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# A class becomes iterable by implementing __iter__, often as a
# generator:
class Countdown:
    def __init__(self, start: int) -> None:
        self.start = start

    def __iter__(self) -> Iterator[int]:
        n = self.start
        while n > 0:
            yield n
            n -= 1


# Any function written against an iterable is decoupled from its
# source:
def total(numbers: Iterable[int]) -> int:
    return sum(numbers)


print(list(fibonacci(8)))
print(list(Countdown(5)))
print(total(fibonacci(8)))   # Works on a generator
print(total([1, 2, 3, 4]))   # and on a list
print(total(Countdown(5)))   # and on a custom iterable
