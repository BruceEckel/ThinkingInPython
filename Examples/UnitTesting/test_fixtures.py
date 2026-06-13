# UnitTesting/test_fixtures.py
from account import Account


def test_deposit_on_any_balance(preloaded: Account, bank_name: str) -> None:
    start = preloaded.balance
    preloaded.deposit(1)
    assert preloaded.balance == start + 1
    assert bank_name  # the session fixture is available everywhere
