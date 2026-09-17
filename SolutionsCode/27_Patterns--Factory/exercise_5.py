# exercise_5.py
from typing import Self
from exceptions import expect
from record import record

@record
class Pizza:
    size: int = 9
    cheese: bool = True
    toppings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.toppings) > 4:
            raise ValueError(
                "a pizza may carry at most four toppings")

expect(ValueError, Pizza,
       toppings=("a", "b", "c", "d", "e"))
#: [ValueError] a pizza may carry at most four toppings

class PizzaBuilder:
    def __init__(self) -> None:
        self._size = 9
        self._toppings: list[str] = []

    def topping(self, name: str) -> Self:
        if len(self._toppings) >= 4:
            raise ValueError(
                "a pizza may carry at most four toppings")
        self._toppings.append(name)
        return self

    def build(self) -> Pizza:
        return Pizza(self._size, True,
                     tuple(self._toppings))

pb = (
    PizzaBuilder().topping("a").topping("b")
    .topping("c").topping("d")
)
expect(ValueError, pb.topping, "e")
#: [ValueError] a pizza may carry at most four toppings
print(pb.build())
#: Pizza(size=9, cheese=True, toppings=('a', 'b', 'c', 'd'))
