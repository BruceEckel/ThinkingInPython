# paper_scissors_rock.py
# Demonstration of multiple dispatching.
from arena import item_pair_gen, match
from outcome import Outcome


class Item:
    def __str__(self):
        return self.__class__.__name__

class Paper(Item):
    def compete(self, item):
        # First dispatch: self was Paper
        return item.eval_paper(self)
    def eval_paper(self, item):
        # Item was Paper, we're in Paper
        return Outcome.DRAW
    def eval_scissors(self, item):
        # Item was Scissors, we're in Paper
        return Outcome.WIN
    def eval_rock(self, item):
        # Item was Rock, we're in Paper
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item):
        # First dispatch: self was Scissors
        return item.eval_scissors(self)
    def eval_paper(self, item):
        # Item was Paper, we're in Scissors
        return Outcome.LOSE
    def eval_scissors(self, item):
        # Item was Scissors, we're in Scissors
        return Outcome.DRAW
    def eval_rock(self, item):
        # Item was Rock, we're in Scissors
        return Outcome.WIN

class Rock(Item):
    def compete(self, item):
        # First dispatch: self was Rock
        return item.eval_rock(self)
    def eval_paper(self, item):
        # Item was Paper, we're in Rock
        return Outcome.WIN
    def eval_scissors(self, item):
        # Item was Scissors, we're in Rock
        return Outcome.LOSE
    def eval_rock(self, item):
        # Item was Rock, we're in Rock
        return Outcome.DRAW

for item1, item2 in item_pair_gen(Item, 20):
    match(item1, item2)
