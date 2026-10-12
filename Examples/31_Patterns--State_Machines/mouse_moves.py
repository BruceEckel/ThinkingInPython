# mouse_moves.py
from typing import Final
from mouse_action import MouseAction as M

MOVES: Final[list[M]] = [
    M.APPEARS, M.RUNS_AWAY, M.APPEARS, M.ENTERS,
    M.ESCAPES, M.APPEARS, M.ENTERS, M.TRAPPED,
    M.REMOVED,
]
