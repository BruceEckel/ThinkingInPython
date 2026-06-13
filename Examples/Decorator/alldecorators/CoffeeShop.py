# Decorator/alldecorators/CoffeeShop.py
# Coffee example using decorators

class DrinkComponent:
    cost: float = 0.0
    def getDescription(self) -> str:
        return self.__class__.__name__
    def getTotalCost(self) -> float:
        return self.__class__.cost

class Mug(DrinkComponent):
    cost = 0.0

class Decorator(DrinkComponent):
    def __init__(self, drinkComponent: DrinkComponent) -> None:
        self.component = drinkComponent
    def getTotalCost(self) -> float:
        return self.component.getTotalCost() + \
          DrinkComponent.getTotalCost(self)
    def getDescription(self) -> str:
        return self.component.getDescription() + \
          ' ' + DrinkComponent.getDescription(self)

class Espresso(Decorator):
    cost = 0.75
    def __init__(self, drinkComponent: DrinkComponent) -> None:
        Decorator.__init__(self, drinkComponent)

class Decaf(Decorator):
    cost = 0.0
    def __init__(self, drinkComponent: DrinkComponent) -> None:
        Decorator.__init__(self, drinkComponent)

class FoamedMilk(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent: DrinkComponent) -> None:
        Decorator.__init__(self, drinkComponent)

class SteamedMilk(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent: DrinkComponent) -> None:
        Decorator.__init__(self, drinkComponent)

class Whipped(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent: DrinkComponent) -> None:
        Decorator.__init__(self, drinkComponent)

class Chocolate(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent: DrinkComponent) -> None:
        Decorator.__init__(self, drinkComponent)

if __name__ == "__main__":
    cappuccino = Espresso(FoamedMilk(Mug()))
    print(cappuccino.getDescription().strip() + ": $" +
          repr(cappuccino.getTotalCost()))

    cafeMocha = Espresso(SteamedMilk(Chocolate(Whipped(Decaf(Mug())))))
    print(cafeMocha.getDescription().strip() + ": $" +
          repr(cafeMocha.getTotalCost()))
