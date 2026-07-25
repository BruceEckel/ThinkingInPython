# typed_generator.py
from collections.abc import Iterable, Iterator

def typed[T](it: Iterable[object], expected: type[T]) -> Iterator[T]:
    for obj in it:
        if not isinstance(obj, expected):
            raise TypeError(
                f"expected {expected}, got {type(obj).__name__}")
        yield obj

if __name__ == "__main__":
    print(list(typed([1, 2, 3], int)))
#: [1, 2, 3]
