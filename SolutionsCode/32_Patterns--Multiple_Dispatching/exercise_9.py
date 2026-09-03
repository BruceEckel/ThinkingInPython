# exercise_9.py
from collections.abc import Callable
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, item: Item) -> Outcome:
        # Look the cell up, then call it:
        return OUTCOME[type(self), type(item)](self, item)
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def __init__(self, wet: bool = False) -> None:
        self.wet = wet
    def __str__(self) -> str:
        return "WetPaper" if self.wet else "Paper"

class Scissors(Item):
    pass
class Rock(Item):
    pass

type Cell = Callable[[Item, Item], Outcome]

def always(outcome: Outcome) -> Cell:
    return lambda item1, item2: outcome

def paper_vs_rock(item1: Item, item2: Item) -> Outcome:
    if isinstance(item1, Paper) and item1.wet:
        return Outcome.DRAW  # Too soggy to wrap a rock
    return Outcome.WIN

OUTCOME: Final[
    dict[tuple[type[Item], type[Item]], Cell]] = {
    (Paper, Rock): paper_vs_rock,
    (Paper, Scissors): always(Outcome.LOSE),
    (Paper, Paper): always(Outcome.DRAW),
    (Scissors, Paper): always(Outcome.WIN),
    (Scissors, Rock): always(Outcome.LOSE),
    (Scissors, Scissors): always(Outcome.DRAW),
    (Rock, Scissors): always(Outcome.WIN),
    (Rock, Paper): always(Outcome.LOSE),
    (Rock, Rock): always(Outcome.DRAW),
}

for item1, item2 in [
    (Paper(), Rock()),
    (Paper(wet=True), Rock()),
    (Scissors(), Paper()),
    (Rock(), Rock()),
]:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
#: Paper <--> Rock : win
#: WetPaper <--> Rock : draw
#: Scissors <--> Paper : win
#: Rock <--> Rock : draw
