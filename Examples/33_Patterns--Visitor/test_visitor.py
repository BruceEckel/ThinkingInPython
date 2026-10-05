# test_visitor.py
import pytest
from visitor_singledispatch import (Chrysanthemum, Flower,
                                    Gladiolus, Ranunculus,
                                    fragrance, nectar)

@pytest.mark.parametrize("flower, expected", [
    (Gladiolus(), "Gladiolus: abundant nectar"),
    (Chrysanthemum(), "Chrysanthemum: a little nectar"),
    (Ranunculus(), "Ranunculus: no nectar"),
    (Flower(), "Flower: no nectar"),
])
def test_nectar_registered_and_default(
    flower: Flower, expected: str
) -> None:
    assert nectar(flower) == expected

@pytest.mark.parametrize("flower, expected", [
    (Ranunculus(), "strong"),
    (Gladiolus(), "faint"),
    (Chrysanthemum(), "faint"),
    (Flower(), "faint"),
])
def test_fragrance_registered_and_default(
    flower: Flower, expected: str
) -> None:
    assert fragrance(flower) == expected

def test_dispatch_follows_inheritance() -> None:
    class Hybrid(Gladiolus):
        pass

    assert Hybrid not in nectar.registry
    assert nectar(Hybrid()) == "Hybrid: abundant nectar"
