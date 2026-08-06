# test_overdraft_message.py
import pytest
from account import Account, InsufficientFunds

def test_overdraft_reports_the_shortfall() -> None:
    account = Account(100)
    with pytest.raises(InsufficientFunds, match="less than 250"):
        account.withdraw(250)
    assert account.balance == 100
