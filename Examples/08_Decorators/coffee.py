# coffee.py
from __future__ import annotations
from typing import Protocol


class Drink(Protocol):
    @property
    def cost(self) -> float: ...
    @property
    def description(self) -> str: ...


class Espresso:
    cost = 1.50
    description = "espresso"


class Cappuccino:
    cost = 1.75
    description = "cappuccino"


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
    name = "whipped cream"


class Decaf(Extra):
    add_cost = 0.0
    name = "decaf"


class ExtraShot(Extra):
    add_cost = 0.75
    name = "extra shot"


if __name__ == "__main__":
    order = Whipped(ExtraShot(Espresso()))
    print(f"{order.description}: ${order.cost:.2f}")

    plain = Cappuccino()
    print(f"{plain.description}: ${plain.cost:.2f}")
