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
