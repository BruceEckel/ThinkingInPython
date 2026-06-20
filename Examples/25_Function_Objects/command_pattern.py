# command_pattern.py
from typing import override


class Command:
    def execute(self) -> None: pass

class Loony(Command):
    @override
    def execute(self) -> None:
        print("You're a loony.")

class NewBrain(Command):
    @override
    def execute(self) -> None:
        print("You might even need a new brain.")

class Afford(Command):
    @override
    def execute(self) -> None:
        print("I couldn't afford a whole new brain.")

# An object that holds commands:
class Macro:
    def __init__(self) -> None:
        self.commands: list[Command] = []
    def add(self, command: Command) -> None:
        self.commands.append(command)
    def run(self) -> None:
        for c in self.commands:
            c.execute()

macro = Macro()
macro.add(Loony())
macro.add(NewBrain())
macro.add(Afford())
macro.run()
