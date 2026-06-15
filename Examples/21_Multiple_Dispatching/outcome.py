# outcome.py
# The win/lose/draw result of one Item competing with another.
from enum import Enum


class Outcome(Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

    def __str__(self):
        return self.value
