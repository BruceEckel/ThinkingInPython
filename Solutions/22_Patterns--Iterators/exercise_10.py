# exercise_10.py
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override
from exceptions import expect

def typed[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for item in items:
        if not isinstance(item, expected):
            raise TypeError(
                f"expected {expected}, "
                f"got {type(item).__name__}")
        yield item

def typed_skipping[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for item in items:
        if isinstance(item, expected):
            yield item

@dataclass(eq=False)
class SkippingIterator[T](Iterator[T]):
    source: Iterator[object]
    expected: type[T]

    @override
    def __next__(self) -> T:
        for item in self.source:  # Pull until one matches
            if isinstance(item, self.expected):
                return item
        raise StopIteration

items: list[object] = [1, "two", 3, None, 4]
expect(TypeError, list, typed(items, int))
#: [TypeError] expected <class 'int'>, got str
print(list(typed_skipping(items, int)))
#: [1, 3, 4]
print(list(SkippingIterator(iter(items), int)))
#: [1, 3, 4]
