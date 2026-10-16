# pizza_order.py
from dataclasses import replace
from pizza_direct import Pizza

pizza = Pizza(size=16, toppings=("basil", "olives"))
print(pizza)
#: Pizza(size=16, cheese=True, toppings=('basil', 'olives'))
family = replace(pizza, size=20)
print(family)
#: Pizza(size=20, cheese=True, toppings=('basil', 'olives'))
