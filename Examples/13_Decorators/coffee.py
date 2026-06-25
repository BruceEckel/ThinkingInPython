# coffee.py
from typing import Protocol

class Drink(Protocol):
    @property
    def cost(self) -> float: ...
    @property
    def description(self) -> str: ...

class Espresso:
    cost = 1.50
    description = "Espresso"

class Cappuccino:
    cost = 1.75
    description = "Cappuccino"

class Extra:
    "Base object decorator: wraps a Drink and adds to it."
    add_cost = 0.0
    name = ""

    def __init__(self, drink: Drink) -> None:
        self.drink = drink

    @property
    def cost(self) -> float:
        return self.drink.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.drink.description} + {self.name}"

class Whipped(Extra):
    add_cost = 0.50
    name = "Whipped cream"

class Decaf(Extra):
    add_cost = 0.0
    name = "Decaf"

class ExtraShot(Extra):
    add_cost = 0.75
    name = "Extra shot"

if __name__ == "__main__":
    order = Whipped(ExtraShot(Espresso()))
    print(f"{order.description}: ${order.cost:.2f}")

    cap = ExtraShot(Decaf(Cappuccino()))
    print(f"{cap.description}: ${cap.cost:.2f}")
## Espresso + Extra shot + Whipped cream: $2.75
## Cappuccino + Decaf + Extra shot: $2.50
