# fibonacci_list.py
from itertools import accumulate, islice, repeat

def fibonacci(n: int) -> list[int]:
    pairs = accumulate(
        repeat(None),
        lambda pair, _: (pair[1], pair[0] + pair[1]),
        initial=(0, 1),
    )
    return [a for a, _ in islice(pairs, n)]

total = 0
for value in fibonacci(7):
    total += value
    print(f"{value=} {total=}")
#: value=0 total=0
#: value=1 total=1
#: value=1 total=2
#: value=2 total=4
#: value=3 total=7
#: value=5 total=12
#: value=8 total=20
