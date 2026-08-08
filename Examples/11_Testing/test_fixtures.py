# test_fixtures.py
from account import Account

def test_deposit_on_any_balance(preloaded: Account) -> None:
    start = preloaded.balance
    preloaded.deposit(1)
    assert preloaded.balance == start + 1

def test_bank_name_is_shared(bank_name: str) -> None:
    assert bank_name == "Crunchy Frog Credit Union"
