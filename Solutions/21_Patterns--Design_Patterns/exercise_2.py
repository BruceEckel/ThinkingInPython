# exercise_2.py
from collections.abc import Callable

type Weight = float
type Cost = float

def flat(weight: Weight) -> Cost:
    return 5.0

def by_weight(weight: Weight) -> Cost:
    return 0.5 * weight

def checkout(
    weight: Weight, shipping: Callable[[Weight], Cost]
) -> Cost:
    return 20.0 + shipping(weight)

print(checkout(6.0, flat), checkout(6.0, by_weight))
#: 25.0 23.0
