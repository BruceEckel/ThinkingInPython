# typed_generator.py
# A generator that type-checks each item as it passes through.
from collections.abc import Iterable, Iterator
from typing import Any


def typed(it: Iterable[Any], expected: type) -> Iterator[Any]:
    for obj in it:
        if not isinstance(obj, expected):
            raise TypeError(
                f"expected {expected}, got {type(obj).__name__}")
        yield obj


if __name__ == "__main__":
    print(list(typed([1, 2, 3], int)))
