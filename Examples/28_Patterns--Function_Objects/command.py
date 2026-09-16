# command.py
from collections.abc import Callable

type Command = Callable[[], None]

def no_more() -> None:
    print("This parrot is no more.")

def ceased() -> None:
    print("It has ceased to be.")

def fjords() -> None:
    print("It's pining for the fjords.")

macro: list[Command] = [no_more, ceased, fjords]
for command in macro:
    command()
#: This parrot is no more.
#: It has ceased to be.
#: It's pining for the fjords.
