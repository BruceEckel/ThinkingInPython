# utils/benchmark.py
import sys
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
