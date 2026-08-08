# exercise_10.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override

def typed[T](it: Iterable[object], expected: type[T]) -> Iterator[T]:
    for obj in it:
        if not isinstance(obj, expected):
            raise TypeError(
                f"expected {expected}, got {type(obj).__name__}")
        yield obj

def typed_skipping[T](
        it: Iterable[object], expected: type[T]) -> Iterator[T]:
    for obj in it:
        if isinstance(obj, expected):
            yield obj

@dataclass(eq=False)
class SkippingIterator[T](Iterator[T]):
    imp: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        for obj in self.imp:  # Pull until one matches
            if isinstance(obj, self.expected):
                return obj
        raise StopIteration

items: list[object] = [1, "two", 3, None, 4]
try:
    print(list(typed(items, int)))
except TypeError as e:
    print(type(e).__name__)
#: TypeError
print(list(typed_skipping(items, int)))
#: [1, 3, 4]
print(list(SkippingIterator(iter(items), int)))
#: [1, 3, 4]
