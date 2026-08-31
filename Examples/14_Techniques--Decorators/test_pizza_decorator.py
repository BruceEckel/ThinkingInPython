# test_pizza_decorator.py
import pytest
from pizza_decorator import Feta, Garlic, Margherita, Olives

def test_stacked_toppings() -> None:
    order = Feta(Olives(Margherita()))
    assert order.cost == pytest.approx(10.00)
    assert order.description == (
        "Margherita + Olives + Feta")

def test_single_topping() -> None:
    order = Garlic(Margherita())
    assert order.cost == pytest.approx(8.50)
    assert order.description == "Margherita + Garlic"
