# account.py
# The unit under test.


class InsufficientFunds(Exception):
    pass


class Account:
    def __init__(self, balance: float = 0.0) -> None:
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise InsufficientFunds(
                f"balance {self.balance} is less than {amount}")
        self.balance -= amount

    def add_interest(self, rate: float) -> None:
        self.balance += self.balance * rate
