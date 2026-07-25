# asking_costs.py
from collections.abc import Iterator

DONE = sentinel("DONE")

def doubled(source: Iterator[int]) -> Iterator[int]:
    # The exception escapes when the source runs out:
    while True:
        yield next(source) * 2

def doubled_ok(source: Iterator[int]) -> Iterator[int]:
    for n in source:  # The loop absorbs the exception
        yield n * 2

numbers = iter([1, 2])
print(next(numbers, DONE) is DONE)  # Asking consumes the 1
#: False
print(next(numbers, DONE) is DONE)  # Asking consumes the 2
#: False
print(next(numbers, DONE) is DONE)  # No more left
#: True

try:
    print(list(doubled(iter([1, 2]))))
except RuntimeError as e:
    print(f"{type(e).__name__}: {e}")
#: RuntimeError: generator raised StopIteration
print(list(doubled_ok(iter([1, 2]))))
#: [2, 4]
