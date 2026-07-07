# exercise_1.py
class UndoableCommand:
    def execute(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError

class Deposit(UndoableCommand):
    def __init__(self, account: dict, amount: int) -> None:
        self.account = account
        self.amount = amount

    def execute(self) -> None:
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
            c.execute()

    def undo_all(self) -> None:
        for c in reversed(self.commands):  # Reverse order to undo
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
