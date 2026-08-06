# eager_validation.py
from collections.abc import Iterator

def squares(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError(f"n must not be negative: {n}")
    def produce() -> Iterator[int]:
        for i in range(n):
            yield i * i
    return produce()

try:
    squares(-1)  # Raises now, not at first next()
except ValueError as e:
    print(e)
#: n must not be negative: -1
