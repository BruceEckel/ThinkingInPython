# paper_scissors_rock.py
import random
from typing import Any
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Paper
        return item.eval_paper(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Paper, and it draws
        return Outcome.DRAW
    def eval_scissors(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Scissors, and it wins
        return Outcome.WIN
    def eval_rock(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Rock, and it loses
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Scissors
        return item.eval_scissors(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Paper, and it loses
        return Outcome.LOSE
    def eval_scissors(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Scissors, and it draws
        return Outcome.DRAW
    def eval_rock(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Rock, and it wins
        return Outcome.WIN

class Rock(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Rock
        return item.eval_rock(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Paper, and it wins
        return Outcome.WIN
    def eval_scissors(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Scissors, and it loses
        return Outcome.LOSE
    def eval_rock(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Rock, and it draws
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
