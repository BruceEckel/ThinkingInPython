# stopwatch.py
import time

def elapsed(start: float) -> float:
    return time.monotonic() - start
