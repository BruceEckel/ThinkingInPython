# bound_method.py
from collections.abc import Callable
from dataclasses import dataclass

type Command = Callable[[], None]

@dataclass
class Account:
    balance: int
    def deposit(self) -> None:
        self.balance += 50
        print(f"balance: {self.balance}")

def alert() -> None:
    print("audit: checking balance")

account = Account(100)
macro: list[Command] = [
    account.deposit, alert, account.deposit,
]
for command in macro:
    command()
#: balance: 150
#: audit: checking balance
#: balance: 200
