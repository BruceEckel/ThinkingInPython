# stopwatch_clock.py
from collections.abc import Callable

def elapsed(start: float,
            now: Callable[[], float]) -> float:
    return now() - start
