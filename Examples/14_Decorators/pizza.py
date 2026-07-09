# pizza.py
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
    "Base object decorator: wraps a Pizza and adds to it."
    add_cost = 0.0
    name = ""

    def __init__(self, pizza: Pizza) -> None:
        self.pizza = pizza

    @property
    def cost(self) -> float:
        return self.pizza.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.pizza.description} + {self.name}"

class Garlic(Topping):
    add_cost = 0.50
    name = "Garlic"

class Olives(Topping):
    add_cost = 0.75
    name = "Olives"

class Feta(Topping):
    add_cost = 1.25
    name = "Feta"

if __name__ == "__main__":
    order = Feta(Olives(Margherita()))
    print(f"{order.description}: ${order.cost:.2f}")

    haw = Garlic(Feta(Hawaiian()))
    print(f"{haw.description}: ${haw.cost:.2f}")
#: Margherita + Olives + Feta: $10.00
#: Hawaiian + Feta + Garlic: $11.25
