# exercise_3.py
from abc import ABC, abstractmethod
from typing import override

class Shipping(ABC):
    @abstractmethod
    def cost(self, weight: float) -> float: ...

class Flat(Shipping):
    @override
    def cost(self, weight: float) -> float:
        return 5.0

class ByWeight(Shipping):
    @override
    def cost(self, weight: float) -> float:
        return 0.5 * weight

def checkout(weight: float, shipping: Shipping) -> float:
    return 20.0 + shipping.cost(weight)

print(checkout(6.0, Flat()), checkout(6.0, ByWeight()))
#: 25.0 23.0
