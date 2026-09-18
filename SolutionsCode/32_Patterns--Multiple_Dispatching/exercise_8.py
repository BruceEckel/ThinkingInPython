# exercise_8.py
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
    "A weapon beats the previous two in the cycle."
    diff = (a.value - b.value) % len(Weapon)
    if diff == 0:
        return Outcome.DRAW
    if diff in (1, 2):
        return Outcome.WIN
    if diff == 3:  # Opposite: neither beats the other
        return Outcome.DRAW
    return Outcome.LOSE

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
class Troll2(Inhabitant2):
    WEAPONS = (Weapon.EDICT, Weapon.SCHEDULE)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = weapon_outcome(
            a.get_weapon(), b.get_weapon())
        if outcome is Outcome.WIN:
            return a
        if outcome is Outcome.LOSE:
            return b
        return None  # Draw: no winner this round

    def meeting(self, group_size: int) -> str:
        kinds = {"Dwarf": Dwarf2, "Elf": Elf2,
                 "Troll": Troll2}
        groups = {
            name: [cls(self.rng) for _ in range(group_size)]
            for name, cls in kinds.items()}
        while sum(1 for g in groups.values() if g) > 1:
            names = [n for n, g in groups.items() if g]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    if not groups[n1] or not groups[n2]:
                        continue
                    winner = self.battle(
                        groups[n1][0], groups[n2][0])
                    if winner is groups[n1][0]:
                        groups[n2].pop(0)
                    elif winner is groups[n2][0]:
                        groups[n1].pop(0)
        survivors = [n for n, g in groups.items() if g]
        return survivors[0]

p2 = Project2(seed=3)
print(p2.meeting(group_size=5))
#: Troll
