# test_printed_balance.py
import io
from contextlib import redirect_stdout
from account import Account

def report(account: Account) -> None:
    print(f"balance: {account.balance:.2f}")

def test_report_prints_balance() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        report(Account(100))
    assert buffer.getvalue() == "balance: 100.00\n"
