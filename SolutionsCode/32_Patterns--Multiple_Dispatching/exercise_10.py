# exercise_10.py
import random
from enum import Enum, StrEnum, auto
from typing import ClassVar

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Weapon(Enum):
    # Definition order is the ranking cycle
    JARGON = auto()
    PLAY = auto()
    INVENT_FEATURE = auto()
    SELL_IMAGINARY_PRODUCT = auto()
    EDICT = auto()
    SCHEDULE = auto()

def weapon_outcome(a: Weapon, b: Weapon) -> Outcome:
    diff = (a.value - b.value) % len(Weapon)
    if diff in (0, 3):  # Same or opposite: no winner
        return Outcome.DRAW
    return Outcome.WIN if diff in (1, 2) else Outcome.LOSE

OUTCOME_TABLE: dict[tuple[Weapon, Weapon], Outcome] = {
    (wa, wb): weapon_outcome(wa, wb)
    for wa in Weapon for wb in Weapon
}

class Inhabitant2:
    WEAPONS: ClassVar[tuple[Weapon, ...]]

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> Weapon:
        return self.rng.choice(self.WEAPONS)

class Dwarf2(Inhabitant2):
    WEAPONS = (Weapon.JARGON, Weapon.PLAY)
class Elf2(Inhabitant2):
    WEAPONS = (Weapon.INVENT_FEATURE,
               Weapon.SELL_IMAGINARY_PRODUCT)

def battle_table(
    a: Inhabitant2, b: Inhabitant2
) -> Inhabitant2 | None:
    outcome = OUTCOME_TABLE[a.get_weapon(), b.get_weapon()]
    if outcome is Outcome.WIN:
        return a
    if outcome is Outcome.LOSE:
        return b
    return None

# Confirm table and formula agree on every combination:
mismatches = [
    (wa, wb) for wa in Weapon for wb in Weapon
    if OUTCOME_TABLE[wa, wb] != weapon_outcome(wa, wb)
]
print(len(OUTCOME_TABLE), "entries, agrees with formula:",
      not mismatches)
#: 36 entries, agrees with formula: True

rng = random.Random(5)
winner = battle_table(Dwarf2(rng), Elf2(rng))
print(isinstance(winner, (Inhabitant2, type(None))))
#: True
