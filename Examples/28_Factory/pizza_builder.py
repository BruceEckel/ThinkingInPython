# pizza_builder.py
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class Pizza:
    size: int
    cheese: bool
    toppings: tuple[str, ...]

class PizzaBuilder:
    def __init__(self) -> None:
        self._size = 12
        self._cheese = True
        self._toppings: list[str] = []

    def size(self, inches: int) -> Self:
        self._size = inches
        return self

    def no_cheese(self) -> Self:
        self._cheese = False
        return self

    def topping(self, name: str) -> Self:
        self._toppings.append(name)
        return self

    def build(self) -> Pizza:
        return Pizza(
            self._size, self._cheese, tuple(self._toppings))

if __name__ == "__main__":
    pizza = (PizzaBuilder()
             .size(16)
             .topping("basil")
             .topping("olives")
             .build())
    print(pizza)
#: Pizza(size=16, cheese=True, toppings=('basil', 'olives'))
