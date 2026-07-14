# pizza_decorator.py
from typing import Protocol

class Pizza(Protocol):
    @property
    def cost(self) -> float: ...
    @property
    def description(self) -> str: ...

class Margherita:
    cost = 8.00
    description = "Margherita"

class Hawaiian:
    cost = 9.50
    description = "Hawaiian"

class Topping:
    add_cost = 0.0

    def __init__(self, pizza: Pizza) -> None:
        self.pizza = pizza
        self.name = type(self).__name__

    @property
    def cost(self) -> float:
        return self.pizza.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.pizza.description} + {self.name}"

class Garlic(Topping):
    add_cost = 0.50

class Olives(Topping):
    add_cost = 0.75

class Feta(Topping):
    add_cost = 1.25

if __name__ == "__main__":
    order = Feta(Olives(Margherita()))
    print(f"{order.description}: ${order.cost:.2f}")

    haw = Garlic(Feta(Hawaiian()))
    print(f"{haw.description}: ${haw.cost:.2f}")
#: Margherita + Olives + Feta: $10.00
#: Hawaiian + Feta + Garlic: $11.25
