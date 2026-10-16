# template_function.py
from collections.abc import Callable

type Step = Callable[[], None]

def run_framework(customize1: Step,
                  customize2: Step = lambda: None) -> None:
    for _ in range(2):  # The anchored algorithm
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

run_framework(lambda: print("one"))
#: one
#: one
