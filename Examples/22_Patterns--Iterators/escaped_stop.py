# escaped_stop.py
from collections.abc import Iterator
from exceptions import expect

def doubled(source: Iterator[int]) -> Iterator[int]:
    # The exception escapes when the source runs out:
    while True:
        yield next(source) * 2

expect(RuntimeError, list, doubled(iter([1, 2])))
#: [RuntimeError] generator raised StopIteration

def doubled_ok(source: Iterator[int]) -> Iterator[int]:
    for n in source:  # The loop absorbs the exception
        yield n * 2

print(list(doubled_ok(iter([1, 2]))))
#: [2, 4]
