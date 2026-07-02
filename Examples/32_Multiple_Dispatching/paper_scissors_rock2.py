# paper_scissors_rock2.py
# Multiple dispatching using a table
from typing import Any, Final
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def compete(self, item: Any) -> Outcome:
        # Use a tuple for table lookup:
        return OUTCOME[self.__class__, item.__class__]
    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass

OUTCOME: Final[dict[tuple[type, type], Outcome]] = {
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

if __name__ == "__main__":
    for item1, item2 in item_pair_gen(Item, 20):
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
