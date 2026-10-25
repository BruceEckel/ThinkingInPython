# fibonacci_iterator.py
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

print(list(Fibonacci(8)))
#: [0, 1, 1, 2, 3, 5, 8, 13]
