# exercise_9.py
from collections.abc import Callable
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        return OUTCOME[type(self), type(opponent)](
            self, opponent)
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
    return lambda player, opponent: outcome

def paper_vs_rock(player: Item, opponent: Item) -> Outcome:
    if isinstance(player, Paper) and player.wet:
        return Outcome.DRAW  # Too soggy to wrap a rock
    return Outcome.WIN

def rock_vs_paper(player: Item, opponent: Item) -> Outcome:
    if isinstance(opponent, Paper) and opponent.wet:
        return Outcome.DRAW  # The same soggy draw
    return Outcome.LOSE

OUTCOME: Final[
    dict[tuple[type[Item], type[Item]], Cell]] = {
    (Paper, Rock): paper_vs_rock,
    (Paper, Scissors): always(Outcome.LOSE),
    (Paper, Paper): always(Outcome.DRAW),
    (Scissors, Paper): always(Outcome.WIN),
    (Scissors, Rock): always(Outcome.LOSE),
    (Scissors, Scissors): always(Outcome.DRAW),
    (Rock, Scissors): always(Outcome.WIN),
    (Rock, Paper): rock_vs_paper,
    (Rock, Rock): always(Outcome.DRAW),
}

for player, opponent in [
    (Paper(), Rock()),
    (Paper(wet=True), Rock()),
    (Rock(), Paper(wet=True)),
    (Scissors(), Paper()),
    (Rock(), Rock()),
]:
    result = player.compete(opponent)
    print(f"{player} <--> {opponent} : {result}")
#: Paper <--> Rock : win
#: WetPaper <--> Rock : draw
#: Rock <--> WetPaper : draw
#: Scissors <--> Paper : win
#: Rock <--> Rock : draw
