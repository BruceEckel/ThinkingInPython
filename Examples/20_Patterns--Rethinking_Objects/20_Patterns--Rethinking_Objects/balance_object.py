# 20_Patterns--Rethinking_Objects/balance_object.py
from dataclasses import dataclass

@dataclass
class Account:
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

if __name__ == "__main__":
    account = Account(100.0)
    account.deposit(50.0)
    account.withdraw(30.0)
    print(account.balance)
#: 120.0
