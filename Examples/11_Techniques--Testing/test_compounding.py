# test_compounding.py
import pytest
from account import Account

def test_interest_compounds() -> None:
    account = Account(100)
    for _ in range(5):
        account.add_interest(0.05)
    assert account.balance == pytest.approx(127.62815625)
