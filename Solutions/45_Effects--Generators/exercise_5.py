# exercise_5.py
from collections.abc import Generator

def emit(items: list[str]) -> Generator[str, None, int]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return total

def report(items: list[str]) -> Generator[str, None, int]:
    size: int = yield from emit(items)
    yield f"({size} characters)"
    return size

def summarize(items: list[str]) -> Generator[str]:
    counted: int = yield from report(items)
    yield f"total: {counted}"

print(list(summarize(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)', 'total: 12']
