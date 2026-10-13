# notifier.py
from collections.abc import Callable

def notify_negative_balance(
    balance: float,
    send: Callable[[str], None],
) -> None:
    if balance < 0:
        send(f"balance is negative: {balance}")
