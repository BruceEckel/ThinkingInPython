# exercise_3.py
from typing import ClassVar, Protocol

class Drink(Protocol):
    @property
    def cost(self) -> float: ...
    @property
    def description(self) -> str: ...

class Espresso:
    cost = 2.50
    description = "Espresso"

class Cappuccino:
    cost = 3.25
    description = "Cappuccino"

class Extra:
    add_cost: ClassVar[float] = 0.0

    def __init__(self, drink: Drink) -> None:
        self.drink = drink
        self.name = type(self).__name__

    @property
    def cost(self) -> float:
        return self.drink.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.drink.description} + {self.name}"

class Whipped(Extra):
    add_cost = 0.75

class Decaf(Extra):
    add_cost = 0.0

class ExtraShot(Extra):
    add_cost = 0.90

order = Whipped(ExtraShot(Espresso()))
print(f"{order.description}: ${order.cost:.2f}")
#: Espresso + ExtraShot + Whipped: $4.15
decaf = Decaf(Cappuccino())
print(f"{decaf.description}: ${decaf.cost:.2f}")
#: Cappuccino + Decaf: $3.25
