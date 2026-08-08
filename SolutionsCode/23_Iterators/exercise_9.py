# exercise_9.py
from collections.abc import Iterator, Sequence

type Nested = int | Sequence[Nested]

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            yield from flatten(item)

def flatten_str(nested: Sequence[Nested]) -> Iterator[int | str]:
    for item in nested:
        if isinstance(item, int | str):  # A str is one item
            yield item
        else:
            yield from flatten_str(item)

mixed: Sequence[Nested] = [1, "ab", 2]
try:
    list(flatten(mixed))
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
print(list(flatten_str(mixed)))
#: [1, 'ab', 2]
print(list(flatten_str([1, ["ab", [2]], 3])))
#: [1, 'ab', 2, 3]
