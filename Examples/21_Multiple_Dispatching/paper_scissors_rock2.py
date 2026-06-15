# paper_scissors_rock2.py
# Multiple dispatching using a table
import random

from outcome import Outcome


class Item:
    def compete(self, item):
        # Use a tuple for table lookup:
        return outcome[self.__class__, item.__class__]
    def __str__(self):
        return self.__class__.__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass

outcome = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
}

def match(item1, item2):
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")

# Generate the items:
def item_pair_gen(n):
    # Create a list of instances of all items:
    items = Item.__subclasses__()
    for i in range(n):
        yield (random.choice(items)(),
               random.choice(items)())

for item1, item2 in item_pair_gen(20):
    match(item1, item2)
