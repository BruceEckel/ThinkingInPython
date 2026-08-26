# test_nailer.py
from typing import Final
import pytest
from nailer import Material, Nailer, holds
from stateless import run, supply

WOOD: Final[Material] = Material(strength=5)
PLASTIC: Final[Material] = Material(strength=10)
HAND: Final[Nailer] = Nailer(force=4)
ROBOTIC: Final[Nailer] = Nailer(force=11)

@pytest.mark.parametrize("material, nailer, expected", [
    (WOOD, HAND, True),
    (PLASTIC, HAND, True),
    (WOOD, ROBOTIC, False),
    (PLASTIC, ROBOTIC, False),
])
def test_holds(
    material: Material, nailer: Nailer, expected: bool
) -> None:
    assert run(
        supply(material, nailer)(holds)()) is expected
