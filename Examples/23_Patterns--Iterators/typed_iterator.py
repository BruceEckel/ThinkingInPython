# typed_iterator.py
from collections.abc import Iterator
from dataclasses import dataclass
from typing import override

@dataclass(eq=False)
class TypedIterator[T](Iterator[T]):
    imp: Iterator[object]
    expected: type[T]
    accepted: int = 0  # State a generator can't expose

    @override
    def __next__(self) -> T:
        obj = next(self.imp)
        if not isinstance(obj, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(obj).__name__}")
        self.accepted += 1
        return obj

if __name__ == "__main__":
    checked = TypedIterator(iter([1, 2, 3]), int)
    print(next(checked), next(checked))
    print(checked.accepted)  # Read mid-stream
#: 1 2
#: 2
