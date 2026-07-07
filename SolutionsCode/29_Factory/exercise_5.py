# exercise_5.py
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class Pizza:
    size: int = 12
    cheese: bool = True
    toppings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.toppings) > 4:
            raise ValueError(
                "a pizza may carry at most four toppings")

try:
    Pizza(toppings=("a", "b", "c", "d", "e"))
except ValueError as e:
    print("direct rejected:", e)
#: direct rejected: a pizza may carry at most four toppings

class PizzaBuilder:
    def __init__(self) -> None:
        self._size = 12
        self._toppings: list[str] = []

    def topping(self, name: str) -> Self:
        if len(self._toppings) >= 4:
            raise ValueError(
                "a pizza may carry at most four toppings")
        self._toppings.append(name)
        return self

    def build(self) -> Pizza:
        return Pizza(self._size, True, tuple(self._toppings))

pb = (
    PizzaBuilder().topping("a").topping("b")
    .topping("c").topping("d")
)
try:
    pb.topping("e")
except ValueError as e:
    print("builder rejected:", e)
#: builder rejected: a pizza may carry at most four toppings
print(pb.build())
#: Pizza(size=12, cheese=True, toppings=('a', 'b', 'c', 'd'))
