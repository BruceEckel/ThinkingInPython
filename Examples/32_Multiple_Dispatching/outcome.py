# outcome.py
# The win/lose/draw result of one Item competing with another.
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
