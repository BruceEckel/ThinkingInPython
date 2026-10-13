# match_dispatch.py
from outcome import Outcome
from paper_scissors_rock_table import Item, Paper, Rock

class Origami(Paper):
    pass

def compete(a: Item, b: Item) -> Outcome:
    match a, b:
        case Paper(), Rock():
            return Outcome.WIN
        case Rock(), Paper():
            return Outcome.LOSE
        case _:
            raise ValueError(f"{a}, {b}")

print(compete(Origami(), Rock()))
#: win
