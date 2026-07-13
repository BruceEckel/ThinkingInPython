# yield_from.py
from collections.abc import Iterator, Sequence

type Nested = int | Sequence[Nested]

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            yield from flatten(item)

print(list(flatten([1, [2, 3], [4, [5, 6]], 7])))
#: [1, 2, 3, 4, 5, 6, 7]
