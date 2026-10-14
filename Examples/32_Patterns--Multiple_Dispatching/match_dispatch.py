# match_dispatch.py
from outcome import Outcome
from paper_scissors_rock_table import Item, Paper, Rock

class Origami(Paper):
    pass

def compete(player: Item, opponent: Item) -> Outcome:
    match player, opponent:
        case Paper(), Rock():
            return Outcome.WIN
        case Rock(), Paper():
            return Outcome.LOSE
        case _:
            raise ValueError(f"{player}, {opponent}")

print(compete(Origami(), Rock()))
#: win
