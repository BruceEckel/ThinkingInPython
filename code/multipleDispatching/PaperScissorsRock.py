# multipleDispatching/PaperScissorsRock.py
# Demonstration of multiple dispatching.
from __future__ import generators
import random

# An enumeration type:
class Outcome:
    def __init__(self, value, name):
        self.value = value
        self.name = name
    def __str__(self): return self.name
    def __eq__(self, other):
        return self.value == other.value

Outcome.WIN = Outcome(0, "win")
Outcome.LOSE = Outcome(1, "lose")
Outcome.DRAW = Outcome(2, "draw")

class Item(object):
    def __str__(self):
        return self.__class__.__name__

class Paper(Item):
    def compete(self, item):
        # First dispatch: self was Paper
        return item.evalPaper(self)
    def evalPaper(self, item):
        # Item was Paper, we're in Paper
        return Outcome.DRAW
    def evalScissors(self, item):
        # Item was Scissors, we're in Paper
        return Outcome.WIN
    def evalRock(self, item):
        # Item was Rock, we're in Paper
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item):
        # First dispatch: self was Scissors
        return item.evalScissors(self)
    def evalPaper(self, item):
        # Item was Paper, we're in Scissors
        return Outcome.LOSE
    def evalScissors(self, item):
        # Item was Scissors, we're in Scissors
        return Outcome.DRAW
    def evalRock(self, item):
        # Item was Rock, we're in Scissors
        return Outcome.WIN

class Rock(Item):
    def compete(self, item):
        # First dispatch: self was Rock
        return item.evalRock(self)
    def evalPaper(self, item):
        # Item was Paper, we're in Rock
        return Outcome.WIN
    def evalScissors(self, item):
        # Item was Scissors, we're in Rock
        return Outcome.LOSE
    def evalRock(self, item):
        # Item was Rock, we're in Rock
        return Outcome.DRAW

def match(item1, item2):
    print("%s <--> %s : %s" % (
      item1, item2, item1.compete(item2)))

# Generate the items:
def itemPairGen(n):
    # Create a list of instances of all Items:
    Items = Item.__subclasses__()
    for i in range(n):
        yield (random.choice(Items)(),
               random.choice(Items)())

for item1, item2 in itemPairGen(20):
    match(item1, item2)