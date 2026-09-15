# command_pattern.py
from typing import override

class Command:
    def execute(self) -> None:
        raise NotImplementedError

class NoMore(Command):
    @override
    def execute(self) -> None:
        print("This parrot is no more.")

class Ceased(Command):
    @override
    def execute(self) -> None:
        print("It has ceased to be.")

class Fjords(Command):
    @override
    def execute(self) -> None:
        print("It's pining for the fjords.")

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
macro.add(NoMore())
macro.add(Ceased())
macro.add(Fjords())
macro.run()
#: This parrot is no more.
#: It has ceased to be.
#: It's pining for the fjords.
