# exercise_5.py
from functools import cache
from exceptions import expect

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

expect(TypeError, deep_sum,
       [1, [2, [3, 4], 5], 6])  # type: ignore
#: [TypeError] unhashable type: 'list'
