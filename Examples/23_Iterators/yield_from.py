# yield_from.py
from collections.abc import Iterator, Sequence

type Nested = int | Sequence[Nested]

def flatten_loop(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            # Spelled out
            for x in flatten_loop(item):  # noqa: UP028
                yield x

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            # The same loop, delegated
            yield from flatten(item)

data: Sequence[Nested] = [1, [2, 3], [4, [5, 6]], 7]
print(list(flatten_loop(data)))
#: [1, 2, 3, 4, 5, 6, 7]
print(list(flatten(data)))
#: [1, 2, 3, 4, 5, 6, 7]
