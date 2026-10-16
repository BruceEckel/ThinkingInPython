# typed_iterator.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass(eq=False)
class TypedIterator[T](Iterator[T]):
    source: Iterator[object]
    expected: type[T]
    # State a generator cannot expose
    accepted: int = field(default=0, init=False)

    @override
    def __next__(self) -> T:
        item = next(self.source)
        if not isinstance(item, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(item).__name__}")
        self.accepted += 1
        return item
