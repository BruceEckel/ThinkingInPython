# paper_scissors_rock_table.py
from typing import Final
from outcome import Outcome

class Item:
    def compete(self, opponent: Item) -> Outcome:
        return OUTCOME[type(self), type(opponent)]
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
