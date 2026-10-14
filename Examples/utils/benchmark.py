# utils/benchmark.py
import sys
import tracemalloc
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Final

NUMBERS: Final[bool] = "--numbers" in sys.argv

def report(**measured: float) -> None:
    # Print each measurement, but only under --numbers:
    if not (NUMBERS and measured):
        return
    width = max(len(name) for name in measured)
    for name, value in measured.items():
        if isinstance(value, int):
            shown = f"{value:,}"  # Byte counts stay whole
        else:
            shown = f"{value:,.6f}"
        print(f"  {name:<{width}} {shown}")

@dataclass
class Traced:
    current: int = 0
    peak: int = 0

@contextmanager
def traced() -> Generator[Traced]:
    measured = Traced()
    tracemalloc.start()
    try:
        yield measured
    finally:
        current, peak = tracemalloc.get_traced_memory()
        measured.current, measured.peak = current, peak
        tracemalloc.stop()
