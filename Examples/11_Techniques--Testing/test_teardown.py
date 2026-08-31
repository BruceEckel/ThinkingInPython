# test_teardown.py
from collections.abc import Iterator
import pytest
from account import Account

@pytest.fixture
def open_account() -> Iterator[Account]:
    account = Account()
    account.deposit(100)
    yield account
    account.withdraw(account.balance)
    assert account.balance == 0

def test_spend_some(open_account: Account) -> None:
    open_account.withdraw(30)
    assert open_account.balance == 70
