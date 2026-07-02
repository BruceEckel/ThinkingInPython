# test_visitor.py
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

def test_fragrance_registered_and_default() -> None:
    assert fragrance(Ranunculus()) == "strong"
    assert fragrance(Gladiolus()) == "faint"
    assert fragrance(Chrysanthemum()) == "faint"

def test_operations_dispatch_independently() -> None:
    # Nectar knows Gladiolus and Chrysanthemum; fragrance knows
    # Ranunculus. A Ranunculus falls to nectar's default but hits
    # fragrance's registered case.
    runuculus = Ranunculus()
    assert nectar(runuculus) == "Ranunculus: no nectar"
    assert fragrance(runuculus) == "strong"
