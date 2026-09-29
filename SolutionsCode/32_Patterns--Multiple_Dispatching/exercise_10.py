# exercise_10.py
import random
from typing import ClassVar, Final
import exercise_8 as methods
from exercise_8 import Outcome

class Weapon:
    def compete(self, item: Weapon) -> Outcome:
        return OUTCOME[type(self), type(item)]
    def __str__(self) -> str:
        return type(self).__name__

class Jargon(Weapon):
    pass
class Play(Weapon):
    pass
class InventFeature(Weapon):
    pass
class SellImaginaryProduct(Weapon):
    pass
class Edict(Weapon):
    pass
class Schedule(Weapon):
    pass

type Table = dict[
    tuple[type[Weapon], type[Weapon]], Outcome]

W: Final[Outcome] = Outcome.WIN
L: Final[Outcome] = Outcome.LOSE
D: Final[Outcome] = Outcome.DRAW
ORDER: Final[tuple[type[Weapon], ...]] = (
    Jargon, Play, InventFeature,
    SellImaginaryProduct, Edict, Schedule)
GRID: Final[tuple[tuple[Outcome, ...], ...]] = (
    (D, L, L, D, W, W),  # Jargon
    (W, D, L, L, D, W),  # Play
    (W, W, D, L, L, D),  # InventFeature
    (D, W, W, D, L, L),  # SellImaginaryProduct
    (L, D, W, W, D, L),  # Edict
    (L, L, D, W, W, D),  # Schedule
)
OUTCOME: Final[Table] = {
    (a, b): cell
    for a, row in zip(ORDER, GRID, strict=True)
    for b, cell in zip(ORDER, row, strict=True)
}

class Inhabitant2:
    WEAPONS: ClassVar[tuple[type[Weapon], ...]]

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> Weapon:
        return self.rng.choice(self.WEAPONS)()

class Dwarf2(Inhabitant2):
    WEAPONS = (Jargon, Play)
class Elf2(Inhabitant2):
    WEAPONS = (InventFeature, SellImaginaryProduct)
class Troll2(Inhabitant2):
    WEAPONS = (Edict, Schedule)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = a.get_weapon().compete(b.get_weapon())
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

def by_methods(a: type[Weapon],
               b: type[Weapon]) -> Outcome:
    return getattr(methods, a.__name__)().compete(
        getattr(methods, b.__name__)())

wrong = [pair for pair, result in OUTCOME.items()
         if by_methods(*pair) != result]
print(len(OUTCOME), "pairs agree with exercise 8:",
      not wrong)
#: 36 pairs agree with exercise 8: True
print(Project2(seed=3).meeting(group_size=5))
#: Troll
