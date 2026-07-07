# test_ch11_invariant.py
import pytest

class InsufficientFunds(Exception):
    def __init__(self, balance: float, amount: float) -> None:
        super().__init__(f"balance {balance} is less than {amount}")

class Account:
    def __init__(self, balance: float = 0.0) -> None:
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise InsufficientFunds(self.balance, amount)
        self.balance -= amount

@pytest.fixture
def never_negative():
    account = Account()
    account.deposit(50)
    yield account
    assert account.balance >= 0

def test_never_negative_after_partial_withdraw(
    never_negative: Account,
) -> None:
    never_negative.withdraw(20)

def test_never_negative_after_deposit(
    never_negative: Account,
) -> None:
    never_negative.deposit(10)
