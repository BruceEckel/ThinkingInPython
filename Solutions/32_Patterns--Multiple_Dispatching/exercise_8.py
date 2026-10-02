# exercise_8.py
import random
from enum import StrEnum
from typing import Any, ClassVar, override

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Weapon:
    def compete(self, item: Any) -> Outcome:
        raise NotImplementedError
    def __str__(self) -> str:
        return type(self).__name__

class Jargon(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_jargon(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.LOSE

class Play(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_play(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.WIN
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.LOSE

class InventFeature(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_invent_feature(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.WIN
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.DRAW

class SellImaginaryProduct(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_sell_imaginary_product(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.WIN

class Edict(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_edict(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.WIN

class Schedule(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_schedule(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.DRAW

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

if __name__ == "__main__":
    print(Play().compete(Jargon()),
          Jargon().compete(Play()),
          Jargon().compete(SellImaginaryProduct()))
    print(Project2(seed=3).meeting(group_size=5))
#: win lose draw
#: Troll
