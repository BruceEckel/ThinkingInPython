# test_overdraft_message.py
import pytest
from account import Account, InsufficientFunds

def test_overdraft_names_amount_keeps_balance() -> None:
    account = Account(100)
    with pytest.raises(InsufficientFunds,
                       match="less than 250"):
        account.withdraw(250)
    assert account.balance == 100
