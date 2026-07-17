# template_function.py
from collections.abc import Callable

def run_framework(customize1: Callable[[], None],
                  customize2: Callable[[], None]) -> None:
    for _ in range(2):  # The fixed algorithm
        customize1()
        customize2()

run_framework(
    lambda: print("Nudge, nudge, wink, wink!"),
    lambda: print("Say no more, say no more!"),
)
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
