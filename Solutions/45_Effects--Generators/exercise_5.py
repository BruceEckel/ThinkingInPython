# exercise_5.py
from collections.abc import Generator
from typing import NewType

Size = NewType("Size", int)

def emit(items: list[str]) -> Generator[str, None, Size]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return Size(total)

def report(items: list[str]) -> Generator[str, None, Size]:
    size: Size = yield from emit(items)
    yield f"({size} characters)"
    return size

def summarize(items: list[str]) -> Generator[str]:
    counted: Size = yield from report(items)
    yield f"total: {counted}"

print(list(summarize(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)', 'total: 12']
