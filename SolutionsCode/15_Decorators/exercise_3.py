# exercise_3.py
class Pizza:
    def cost(self) -> float:
        raise NotImplementedError

    def description(self) -> str:
        raise NotImplementedError

class Margherita(Pizza):
    def cost(self) -> float:
        return 8.0

    def description(self) -> str:
        return "Margherita"

class Hawaiian(Pizza):
    def cost(self) -> float:
        return 9.0

    def description(self) -> str:
        return "Hawaiian"

class ToppingDecorator(Pizza):
    def __init__(self, pizza: Pizza) -> None:
        self.pizza = pizza

class Garlic(ToppingDecorator):
    def cost(self) -> float:
        return self.pizza.cost() + 0.5

    def description(self) -> str:
        return self.pizza.description() + " + Garlic"

class Olives(ToppingDecorator):
    def cost(self) -> float:
        return self.pizza.cost() + 0.75

    def description(self) -> str:
        return self.pizza.description() + " + Olives"

class Feta(ToppingDecorator):
    def cost(self) -> float:
        return self.pizza.cost() + 1.0

    def description(self) -> str:
        return self.pizza.description() + " + Feta"

pizza = Feta(Olives(Margherita()))
print(f"{pizza.description()}: ${pizza.cost():.2f}")
#: Margherita + Olives + Feta: $9.75
