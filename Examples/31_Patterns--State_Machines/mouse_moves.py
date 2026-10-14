# mouse_moves.py
from typing import Final
from mouse import Mouse

MOVES: Final[list[Mouse]] = [
    Mouse.APPEARS, Mouse.RUNS_AWAY, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.ESCAPES, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.TRAPPED, Mouse.REMOVED,
]
