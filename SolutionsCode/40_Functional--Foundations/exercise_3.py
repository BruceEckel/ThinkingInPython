# exercise_3.py
from collections.abc import Callable

def multiplier(factor: int) -> Callable[[int], int]:
    def multiply(n: int) -> int:
        return n * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
quadruple = multiplier(4)
print(double(10), triple(10), quadruple(10))
#: 20 30 40
