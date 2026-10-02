# exercise_1.py
from collections.abc import Iterable, Iterator

def total(numbers: Iterable[int]) -> int:
    return sum(numbers)

def evens(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * 2

print(list(evens(5)))
#: [0, 2, 4, 6, 8]
print(total(evens(5)))
#: 20
