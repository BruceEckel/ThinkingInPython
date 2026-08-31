# pizza_direct.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Pizza:
    size: int = 12
    cheese: bool = True
    toppings: tuple[str, ...] = ()

if __name__ == "__main__":
    pizza = Pizza(size=16, toppings=("basil", "olives"))
    print(pizza)
    family = replace(pizza, size=20)
    print(family)
#: Pizza(size=16, cheese=True, toppings=('basil', 'olives'))
#: Pizza(size=20, cheese=True, toppings=('basil', 'olives'))
