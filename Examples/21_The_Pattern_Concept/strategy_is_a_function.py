# strategy_is_a_function.py
from collections.abc import Callable

def apply(nums: list[int], how: Callable[[list[int]], int]) -> int:
    return how(nums)
print(apply([3, 1, 2], max), apply([3, 1, 2], sum))
#: 3 6
