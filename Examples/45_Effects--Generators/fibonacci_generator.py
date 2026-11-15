# fibonacci_generator.py
from collections.abc import Iterator

def fibonacci(n: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(n):
        print(f"computed {a}")
        yield a
        a, b = b, a + b

total = 0
for value in fibonacci(7):
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
