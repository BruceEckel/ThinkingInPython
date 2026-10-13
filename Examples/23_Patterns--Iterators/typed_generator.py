# typed_generator.py
from collections.abc import Iterable, Iterator

def typed[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for item in items:
        if not isinstance(item, expected):
            raise TypeError(
                f"expected {expected}, "
                f"got {type(item).__name__}")
        yield item
