# test_pizza.py
from dataclasses import replace
import pizza_builder as pb
import pizza_direct as pd

def test_builder_and_keywords_agree() -> None:
    built = (pb.PizzaBuilder()
             .size(16).topping("basil").build())
    direct = pd.Pizza(size=16, toppings=("basil",))
    assert (built.size, built.cheese, built.toppings) == (
        direct.size, direct.cheese, direct.toppings)

def test_replace_varies_one_field() -> None:
    base = pd.Pizza()
    variant = replace(base, size=18)
    assert base.size == 12 and variant.size == 18
    assert variant.toppings == base.toppings

def test_second_build_reuses_toppings() -> None:
    builder = pb.PizzaBuilder().topping("basil")
    first = builder.build()
    second = builder.topping("olives").build()
    assert first.toppings == ("basil",)
    assert second.toppings == ("basil", "olives")
