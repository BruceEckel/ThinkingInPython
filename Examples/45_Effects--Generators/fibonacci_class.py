# fibonacci_class.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass
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
        print(f"computed {value}")
        return value

total = 0
for value in Fibonacci(7):
    total += value
    print(f"{value=} {total=}")
#: computed 0
#: value=0 total=0
#: computed 1
#: value=1 total=1
#: computed 1
#: value=1 total=2
#: computed 2
#: value=2 total=4
#: computed 3
#: value=3 total=7
#: computed 5
#: value=5 total=12
#: computed 8
#: value=8 total=20
