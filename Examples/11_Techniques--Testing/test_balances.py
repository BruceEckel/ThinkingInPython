# test_balances.py
import pytest
from account import Account

@pytest.mark.parametrize("start, spend, expected", [
    (100, 40, 60),
    (50, 50, 0),
    (200, 1, 199),
])
def test_withdraw_leaves_expected_balance(
    start: float, spend: float, expected: float
) -> None:
    account = Account(start)
    account.withdraw(spend)
    assert account.balance == expected
