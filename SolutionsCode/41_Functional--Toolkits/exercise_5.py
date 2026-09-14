# exercise_5.py
from functools import cache

type Nested = int | list[Nested]

@cache
def deep_sum(items: list[Nested]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)  # type: ignore
        else:
            total += item
    return total

try:
    deep_sum([1, [2, [3, 4], 5], 6])  # type: ignore
except TypeError as e:
    print(f"{type(e).__name__}: {e}")
#: TypeError: unhashable type: 'list'
