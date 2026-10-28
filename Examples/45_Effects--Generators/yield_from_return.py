# yield_from_return.py
from collections.abc import Generator, Iterator

type Size = int

def emit(items: list[str]) -> Generator[str, None, Size]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return total

def report(items: list[str]) -> Iterator[str]:
    size: Size = yield from emit(items)
    yield f"({size} characters)"

print(list(report(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)']
