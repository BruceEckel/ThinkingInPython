# typed_iterator.py
from collections.abc import Iterator
from typing import override

class TypedIterator[T](Iterator[T]):
    def __init__(self, it: Iterator[object],
                 expected: type[T]) -> None:
        self.imp = it
        self.expected = expected

    @override
    def __next__(self) -> T:
        obj = next(self.imp)
        if not isinstance(obj, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(obj).__name__}")
        return obj
