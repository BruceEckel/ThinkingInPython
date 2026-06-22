# command.py
# A function is already a command object; a macro is a list of them.
from collections.abc import Callable

def loony() -> None:
    print("You're a loony.")

def new_brain() -> None:
    print("You might even need a new brain.")

def afford() -> None:
    print("I couldn't afford a whole new brain.")

macro: list[Callable[[], None]] = [loony, new_brain, afford]
for command in macro:
    command()
