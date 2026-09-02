# exercise_5.py
from functools import cache

type Nested = int | list[Nested]

@cache
def deep_sum(items: list[Nested]) -> int:
    return 0

try:
    deep_sum([1, [2, 3]])  # type: ignore
except TypeError as e:
    print(f"{type(e).__name__}: {e}")
#: TypeError: unhashable type: 'list'
