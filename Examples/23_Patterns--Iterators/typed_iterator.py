# typed_iterator.py
from collections.abc import Iterator
from dataclasses import dataclass
from typing import override

@dataclass(eq=False)
class TypedIterator[T](Iterator[T]):
    imp: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        obj = next(self.imp)
        if not isinstance(obj, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(obj).__name__}")
        return obj
