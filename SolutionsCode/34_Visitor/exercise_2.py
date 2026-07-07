# exercise_2.py
import random
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

WEAPON_ORDER = ["Jargon", "Play", "InventFeature",
                "SellImaginaryProduct", "Edict", "Schedule"]
WEAPON_INDEX = {name: i for i, name in enumerate(WEAPON_ORDER)}

WEAPONS_BY_KIND = {
    "Dwarf": ["Jargon", "Play"],
    "Elf": ["InventFeature", "SellImaginaryProduct"],
    "Troll": ["Edict", "Schedule"],
}

def weapon_outcome(a: str, b: str) -> Outcome:
    "A weapon beats the next two in WEAPON_ORDER (cyclically)."
    ia, ib = WEAPON_INDEX[a], WEAPON_INDEX[b]
    diff = (ia - ib) % 6
    if diff == 0:
        return Outcome.DRAW
    if diff in (1, 2):
        return Outcome.WIN
    return Outcome.LOSE

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
class Troll2(Inhabitant2):
    KIND = "Troll"

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = weapon_outcome(a.get_weapon(), b.get_weapon())
        if outcome is Outcome.WIN:
            return a
        if outcome is Outcome.LOSE:
            return b
        return None  # Draw: no winner this round

    def meeting(self, group_size: int) -> str:
        kinds = {"Dwarf": Dwarf2, "Elf": Elf2, "Troll": Troll2}
        groups = {name: [cls(self.rng) for _ in range(group_size)]
                  for name, cls in kinds.items()}
        while sum(1 for g in groups.values() if g) > 1:
            names = [n for n, g in groups.items() if g]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    if not groups[n1] or not groups[n2]:
                        continue
                    winner = self.battle(groups[n1][0], groups[n2][0])
                    if winner is groups[n1][0]:
                        groups[n2].pop(0)
                    elif winner is groups[n2][0]:
                        groups[n1].pop(0)
        survivors = [n for n, g in groups.items() if g]
        return survivors[0]

p2 = Project2(seed=3)
print(p2.meeting(group_size=5))
#: Troll
