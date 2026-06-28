# clock.py
from collections.abc import Callable

def stamp(now: Callable[[], float]) -> float:
    return now()
