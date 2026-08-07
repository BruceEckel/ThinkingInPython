# test_ch46_nailer.py
from dataclasses import dataclass
from typing import Final
import pytest
from stateless import Depend, Need, need, run, supply

@dataclass(frozen=True)
class Material:
    strength: int

@dataclass(frozen=True)
class Nailer:
    force: int

def holds() -> Depend[Need[Material] | Need[Nailer], bool]:
    material = yield from need(Material)
    nailer = yield from need(Nailer)
    return nailer.force < material.strength

WOOD: Final[Material] = Material(strength=5)
PLASTIC: Final[Material] = Material(strength=10)
METAL: Final[Material] = Material(strength=20)
HAND: Final[Nailer] = Nailer(force=4)
ROBOTIC: Final[Nailer] = Nailer(force=11)

@pytest.mark.parametrize("material, nailer, expected", [
    (WOOD, HAND, True),
    (PLASTIC, HAND, True),
    (METAL, HAND, True),
    (WOOD, ROBOTIC, False),
    (PLASTIC, ROBOTIC, False),
    (METAL, ROBOTIC, True),
])
def test_holds(
    material: Material, nailer: Nailer, expected: bool
) -> None:
    assert run(supply(material, nailer)(holds)()) is expected

print(run(supply(METAL, ROBOTIC)(holds)()))
#: True
