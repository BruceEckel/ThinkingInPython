# bound_method.py
from collections.abc import Callable

class Account:
    def __init__(self, balance: int) -> None:
        self.balance = balance
    def deposit(self) -> None:
        self.balance += 50
        print(f"balance: {self.balance}")

def alert() -> None:
    print("audit: checking balance")

account = Account(100)
macro: list[Callable[[], None]] = [
    account.deposit, alert, account.deposit,
]
for command in macro:
    command()
#: balance: 150
#: audit: checking balance
#: balance: 200
