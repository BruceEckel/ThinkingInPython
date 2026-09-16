# exercise_1.py
from typing import Protocol

class UndoableCommand(Protocol):
    def __call__(self) -> None: ...
    def undo(self) -> None: ...

class Deposit:
    def __init__(self, account: dict, amount: int) -> None:
        self.account = account
        self.amount = amount

    def __call__(self) -> None:
        self.account["balance"] += self.amount

    def undo(self) -> None:
        self.account["balance"] -= self.amount

class Macro:
    def __init__(self) -> None:
        self.commands: list[UndoableCommand] = []

    def add(self, command: UndoableCommand) -> None:
        self.commands.append(command)

    def run(self) -> None:
        for c in self.commands:
            c()

    def undo_all(self) -> None:
        # Reverse order to undo
        for c in reversed(self.commands):
            c.undo()

account = {"balance": 0}
macro = Macro()
macro.add(Deposit(account, 10))
macro.add(Deposit(account, 5))
macro.run()
print(account["balance"])
#: 15
macro.undo_all()
print(account["balance"])
#: 0
