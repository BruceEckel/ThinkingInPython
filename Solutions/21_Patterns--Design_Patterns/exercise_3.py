# exercise_3.py
from abc import ABC, abstractmethod
from typing import override

type Weight = float
type Cost = float

class Shipping(ABC):
    @abstractmethod
    def cost(self, weight: Weight) -> Cost: ...

class Flat(Shipping):
    @override
    def cost(self, weight: Weight) -> Cost:
        return 5.0

class ByWeight(Shipping):
    @override
    def cost(self, weight: Weight) -> Cost:
        return 0.5 * weight

def checkout(weight: Weight, shipping: Shipping) -> Cost:
    return 20.0 + shipping.cost(weight)

print(checkout(6.0, Flat()), checkout(6.0, ByWeight()))
#: 25.0 23.0
