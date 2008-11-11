# decorator/alldecorators/CoffeeShop.py
# Coffee example using decorators

class DrinkComponent:
    def getDescription(self):
        return self.__class__.__name__
    def getTotalCost(self):
        return self.__class__.cost

class Mug(DrinkComponent):
    cost = 0.0

class Decorator(DrinkComponent):
    def __init__(self, drinkComponent):
        self.component = drinkComponent
    def getTotalCost(self):
        return self.component.getTotalCost() + \
          DrinkComponent.getTotalCost(self)
    def getDescription(self):
        return self.component.getDescription() + \
          ' ' + DrinkComponent.getDescription(self)

class Espresso(Decorator):
    cost = 0.75
    def __init__(self, drinkComponent):
        Decorator.__init__(self, drinkComponent)

class Decaf(Decorator):
    cost = 0.0
    def __init__(self, drinkComponent):
        Decorator.__init__(self, drinkComponent)

class FoamedMilk(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent):
        Decorator.__init__(self, drinkComponent)

class SteamedMilk(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent):
        Decorator.__init__(self, drinkComponent)

class Whipped(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent):
        Decorator.__init__(self, drinkComponent)

class Chocolate(Decorator):
    cost = 0.25
    def __init__(self, drinkComponent):
        Decorator.__init__(self, drinkComponent)

cappuccino = Espresso(FoamedMilk(Mug()))
print(cappuccino.getDescription().strip() + \)
  ": $" + `cappuccino.getTotalCost()`

cafeMocha = Espresso(SteamedMilk(Chocolate(
  Whipped(Decaf(Mug())))))

print(cafeMocha.getDescription().strip() + \)
  ": $" + `cafeMocha.getTotalCost()`