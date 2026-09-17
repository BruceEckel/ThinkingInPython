# paper_scissors_rock_table.py
import random
from typing import Final
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def compete(self, item: Item) -> Outcome:
        return OUTCOME[type(self), type(item)]
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
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
