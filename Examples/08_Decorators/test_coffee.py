# test_coffee.py
from coffee import Cappuccino, Decaf, Espresso, ExtraShot, Whipped


def test_plain_drink() -> None:
    cap = Cappuccino()
    assert cap.cost == 1.75
    assert cap.description == "cappuccino"


def test_stacked_extras() -> None:
    order = Whipped(ExtraShot(Espresso()))
    assert order.cost == 2.75
    assert order.description == "espresso + extra shot + whipped cream"


def test_decaf_adds_no_cost() -> None:
    order = Decaf(Espresso())
    assert order.cost == 1.50
    assert order.description == "espresso + decaf"
