# Decorator/alldecorators/EspressoDecorator.py
from CoffeeShop import Decorator, DrinkComponent


class Espresso(Decorator):
    cost = 0.75
    description = " espresso"
    def __init__(self, component: DrinkComponent) -> None:
        Decorator.__init__(self, component)

    def getTotalCost(self) -> float:
        return self.component.getTotalCost() + self.cost

    def getDescription(self) -> str:
        return self.component.getDescription() + self.description
