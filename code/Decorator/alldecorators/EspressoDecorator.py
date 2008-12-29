# Decorator/alldecorators/EspressoDecorator.py

class Espresso(Decorator):
    cost = 0.75f
    description = " espresso"
    def __init__(DrinkComponent):
        Decorator.__init__(self, component)

    def getTotalCost(self):
        return self.component.getTotalCost() + cost

    def getDescription(self):
        return self.component.getDescription() +
            description