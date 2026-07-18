# test_visitor.py
import pytest
from visitor_singledispatch import (
    Chrysanthemum,
    Flower,
    Gladiolus,
    Ranunculus,
    fragrance,
    nectar,
)

def test_nectar_registered_types() -> None:
    assert nectar(Gladiolus()) == "Gladiolus: abundant nectar"
    assert nectar(Chrysanthemum()) == "Chrysanthemum: a little nectar"

def test_nectar_default_for_unregistered() -> None:
    assert nectar(Ranunculus()) == "Ranunculus: no nectar"
    assert nectar(Flower()) == "Flower: no nectar"

@pytest.mark.parametrize("flower, expected", [
    (Ranunculus(), "strong"),
    (Gladiolus(), "faint"),
    (Chrysanthemum(), "faint"),
])
def test_fragrance_registered_and_default(
    flower: Flower, expected: str
) -> None:
    assert fragrance(flower) == expected

def test_operations_dispatch_independently() -> None:
    # Nectar knows Gladiolus and Chrysanthemum; fragrance knows
    # Ranunculus. A Ranunculus falls to nectar's default but hits
    # fragrance's registered case.
    ranunculus = Ranunculus()
    assert nectar(ranunculus) == "Ranunculus: no nectar"
    assert fragrance(ranunculus) == "strong"

def test_dispatch_follows_inheritance() -> None:
    # Unregistered subclass: nearest registered ancestor wins
    class Hybrid(Gladiolus):
        pass

    assert nectar(Hybrid()) == "Hybrid: abundant nectar"
