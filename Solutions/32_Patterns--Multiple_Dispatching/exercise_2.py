# exercise_2.py
from enum import StrEnum
from typing import Any

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_paper(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.DRAW

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.WIN

class Scissors(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_scissors(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.DRAW

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.WIN

class Rock(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_rock(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.DRAW

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.LOSE

class Lizard(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_lizard(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.DRAW

if __name__ == "__main__":
    print(Lizard().compete(Paper()),
          Lizard().compete(Scissors()),
          Lizard().compete(Rock()),
          Lizard().compete(Lizard()))
#: win win lose draw
