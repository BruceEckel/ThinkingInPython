# paper_scissors_rock.py
import random
from typing import Any
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Paper
        return item.eval_paper(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper; this is Paper's case
        return Outcome.DRAW
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors; this is Paper's case
        return Outcome.WIN
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock; this is Paper's case
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Scissors
        return item.eval_scissors(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper; this is Scissors' case
        return Outcome.LOSE
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors; this is Scissors' case
        return Outcome.DRAW
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock; this is Scissors' case
        return Outcome.WIN

class Rock(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Rock
        return item.eval_rock(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper; this is Rock's case
        return Outcome.WIN
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors; this is Rock's case
        return Outcome.LOSE
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock; this is Rock's case
        return Outcome.DRAW

if __name__ == "__main__":
    random.seed(47)  # Reproducible pairs
    for item1, item2 in item_pair_gen(Item, 10):
        duel(item1, item2)
#: Scissors <--> Paper : win
#: Scissors <--> Rock : lose
#: Scissors <--> Rock : lose
#: Scissors <--> Scissors : draw
#: Rock <--> Scissors : win
#: Scissors <--> Rock : lose
#: Paper <--> Scissors : lose
#: Rock <--> Paper : lose
#: Paper <--> Paper : draw
#: Scissors <--> Scissors : draw
