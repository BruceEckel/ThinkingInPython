# Util/TypedIterator.py
from collections.abc import Iterator
from typing import Any


class TypedIterator(Iterator[Any]):
    def __init__(self, it: Iterator[Any], expected: type) -> None:
        self.imp = it
        self.expected = expected

    def __next__(self) -> Any:
        obj = next(self.imp)
        if not isinstance(obj, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(obj).__name__}")
        return obj
