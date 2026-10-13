# strategy_is_a_function.py
from collections.abc import Callable

def apply(nums: list[int],
          strategy: Callable[[list[int]], int]) -> int:
    return strategy(nums)
nums = [3, 1, 2]
for strategy in (max, sum):
    print(strategy.__name__, apply(nums, strategy))
#: max 3
#: sum 6
