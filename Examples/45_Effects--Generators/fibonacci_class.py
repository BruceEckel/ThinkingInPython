# fibonacci_class.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass(eq=False)
class Fibonacci(Iterator[int]):
    remaining: int
    _a: int = field(default=0, init=False)
    _b: int = field(default=1, init=False)

    @override
    def __next__(self) -> int:
        if self.remaining == 0:
            raise StopIteration
        self.remaining -= 1
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        return value

total = 0
for value in Fibonacci(7):
    total += value
    print(f"{value=} {total=}")
#: value=0 total=0
#: value=1 total=1
#: value=1 total=2
#: value=2 total=4
#: value=3 total=7
#: value=5 total=12
#: value=8 total=20
