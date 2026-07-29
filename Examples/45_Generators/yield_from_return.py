# yield_from_return.py
from collections.abc import Generator, Iterator

def emit(items: list[str]) -> Generator[str, None, int]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return total

def report(items: list[str]) -> Iterator[str]:
    size: int = yield from emit(items)
    yield f"({size} characters)"

print(list(report(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)']
