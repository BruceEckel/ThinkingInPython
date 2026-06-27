# paper_scissors_rock.py
# Demonstration of multiple dispatching.
from typing import Any
from arena import item_pair_gen, match
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Paper
        return item.eval_paper(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper, we're in Paper
        return Outcome.DRAW
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors, we're in Paper
        return Outcome.WIN
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock, we're in Paper
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Scissors
        return item.eval_scissors(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper, we're in Scissors
        return Outcome.LOSE
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors, we're in Scissors
        return Outcome.DRAW
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock, we're in Scissors
        return Outcome.WIN

class Rock(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Rock
        return item.eval_rock(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper, we're in Rock
        return Outcome.WIN
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors, we're in Rock
        return Outcome.LOSE
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock, we're in Rock
        return Outcome.DRAW

if __name__ == "__main__":
    for item1, item2 in item_pair_gen(Item, 20):
        match(item1, item2)
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
#: Rock <--> Rock : draw
#: Paper <--> Scissors : lose
#: Rock <--> Scissors : win
#: Paper <--> Paper : draw
#: Rock <--> Rock : draw
#: Scissors <--> Scissors : draw
#: Paper <--> Paper : draw
#: Rock <--> Scissors : win
#: Rock <--> Rock : draw
#: Scissors <--> Rock : lose
