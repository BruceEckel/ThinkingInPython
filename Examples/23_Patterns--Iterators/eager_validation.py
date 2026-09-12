# eager_validation.py
from collections.abc import Iterator
from exceptions import expect

def squares(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError(f"n must not be negative: {n}")
    def produce() -> Iterator[int]:
        for i in range(n):
            yield i * i
    return produce()

# Raises now, not at first next():
expect(ValueError, squares, -1)
#: [ValueError] n must not be negative: -1
