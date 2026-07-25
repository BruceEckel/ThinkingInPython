# asking_costs.py
from collections.abc import Iterator
from typing import Final

DONE: Final[object] = object()

def doubled(source: Iterator[int]) -> Iterator[int]:
    while True:
        yield next(source) * 2  # Escapes when source runs out

def doubled_ok(source: Iterator[int]) -> Iterator[int]:
    for n in source:  # The loop absorbs the exception
        yield n * 2

numbers = iter([1, 2])
print(next(numbers, DONE) is DONE)  # Asking consumed the 1
#: False
print(next(numbers, DONE) is DONE)
#: False
print(next(numbers, DONE) is DONE)  # Now the answer is yes
#: True

try:
    print(list(doubled(iter([1, 2]))))
except RuntimeError as e:
    print(f"{type(e).__name__}: {e}")
#: RuntimeError: generator raised StopIteration
print(list(doubled_ok(iter([1, 2]))))
#: [2, 4]
