# closures.py
import inspect
from collections.abc import Callable

def multiplier(factor: int) -> Callable[[int], int]:
    # The inner function captures factor from this scope:
    def multiply(n: int) -> int:
        return n * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
print(double(10), triple(10))
#: 20 30
print(inspect.getclosurevars(double).nonlocals)
#: {'factor': 2}
print(inspect.getclosurevars(triple).nonlocals)
#: {'factor': 3}
