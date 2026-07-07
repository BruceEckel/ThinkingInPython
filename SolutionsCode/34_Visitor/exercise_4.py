# exercise_4.py
import random
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

WEAPON_ORDER = ["Jargon", "Play", "InventFeature",
                "SellImaginaryProduct", "Edict", "Schedule"]

WEAPONS_BY_KIND = {
    "Dwarf": ["Jargon", "Play"],
    "Elf": ["InventFeature", "SellImaginaryProduct"],
    "Troll": ["Edict", "Schedule"],
}

def weapon_outcome(a: str, b: str) -> Outcome:
    order = WEAPON_ORDER
    diff = (order.index(a) - order.index(b)) % 6
    if diff == 0:
        return Outcome.DRAW
    return Outcome.WIN if diff in (1, 2) else Outcome.LOSE

OUTCOME_TABLE: dict[tuple[str, str], Outcome] = {
    (wa, wb): weapon_outcome(wa, wb)
    for wa in WEAPON_ORDER for wb in WEAPON_ORDER
}

class Inhabitant2:
    KIND: str = ""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> str:
        return self.rng.choice(WEAPONS_BY_KIND[self.KIND])

class Dwarf2(Inhabitant2):
    KIND = "Dwarf"
class Elf2(Inhabitant2):
    KIND = "Elf"

def battle_table(
    a: Inhabitant2, b: Inhabitant2
) -> Inhabitant2 | None:
    outcome = OUTCOME_TABLE[a.get_weapon(), b.get_weapon()]
    if outcome is Outcome.WIN:
        return a
    if outcome is Outcome.LOSE:
        return b
    return None

# Confirm the table agrees with the formula on every combination:
mismatches = [
    (wa, wb) for wa in WEAPON_ORDER for wb in WEAPON_ORDER
    if OUTCOME_TABLE[wa, wb] != weapon_outcome(wa, wb)
]
print(len(OUTCOME_TABLE), "entries, agrees with formula:",
      not mismatches)
#: 36 entries, agrees with formula: True

rng = random.Random(5)
winner = battle_table(Dwarf2(rng), Elf2(rng))
print(isinstance(winner, (Inhabitant2, type(None))))
#: True
