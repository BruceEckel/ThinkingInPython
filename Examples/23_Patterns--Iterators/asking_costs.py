# asking_costs.py
from collections.abc import Iterator
from exceptions import expect

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

expect(RuntimeError, list, doubled(iter([1, 2])))
#: [RuntimeError] generator raised StopIteration
print(list(doubled_ok(iter([1, 2]))))
#: [2, 4]
