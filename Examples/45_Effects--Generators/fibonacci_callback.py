# fibonacci_callback.py
from collections.abc import Callable

def fibonacci(
    n: int, callback: Callable[[int], None]
) -> None:
    a, b = 0, 1
    for _ in range(n):
        print(f"computed {a}")
        callback(a)
        a, b = b, a + b

def summing() -> Callable[[int], None]:
    total = 0
    def consume(value: int) -> None:
        nonlocal total
        if total > 10:
            return
        total += value
        print(f"{value=} {total=}")
    return consume

fibonacci(7, summing())
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
