# exercise_6.py
from collections.abc import Callable
from functools import partial

type Command = Callable[[], None]

broken: list[Command] = []
for n in range(3):
    broken.append(lambda: print(n))
for command in broken:
    command()
#: 2
#: 2
#: 2

by_default: list[Command] = []
for n in range(3):
    by_default.append(lambda n=n: print(n))

by_partial: list[Command] = []
for n in range(3):
    by_partial.append(partial(print, n))

def make(n: int) -> Command:
    return lambda: print(n)

by_factory: list[Command] = [
    make(n) for n in range(3)
]

for fixed in (by_default, by_partial, by_factory):
    for command in fixed:
        command()
#: 0
#: 1
#: 2
#: 0
#: 1
#: 2
#: 0
#: 1
#: 2

# Late lookup, kept on purpose:
settings = {"level": "low"}

def report() -> None:
    print(settings["level"])

settings["level"] = "high"
report()
#: high
