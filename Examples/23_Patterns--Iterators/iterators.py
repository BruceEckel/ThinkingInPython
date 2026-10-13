# iterators.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

def fibonacci(n: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

@dataclass
class Countdown:
    start: int

    def __iter__(self) -> Iterator[int]:
        n = self.start
        while n > 0:
            yield n
            n -= 1

def total(numbers: Iterable[int]) -> int:
    return sum(numbers)
