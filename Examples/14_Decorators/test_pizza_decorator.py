# test_pizza_decorator.py
from pizza_decorator import Feta, Garlic, Hawaiian, Margherita, Olives

def test_plain_pizza() -> None:
    pizza = Hawaiian()
    assert pizza.cost == 9.50
    assert pizza.description == "Hawaiian"

def test_stacked_toppings() -> None:
    order = Feta(Olives(Margherita()))
    assert order.cost == 10.00
    assert order.description == (
        "Margherita + Olives + Feta")

def test_single_topping() -> None:
    order = Garlic(Margherita())
    assert order.cost == 8.50
    assert order.description == "Margherita + Garlic"
