# exercise_2.py
from collections.abc import Callable

def flat(weight: float) -> float:
    return 5.0

def by_weight(weight: float) -> float:
    return 0.5 * weight

def checkout(
    weight: float, shipping: Callable[[float], float]
) -> float:
    return 20.0 + shipping(weight)

print(checkout(6.0, flat), checkout(6.0, by_weight))
#: 25.0 23.0
