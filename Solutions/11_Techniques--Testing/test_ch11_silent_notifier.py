# test_ch11_silent_notifier.py
from collections.abc import Callable
from unittest.mock import Mock
import pytest

def notify_low_balance(
    balance: float,
    send: Callable[[str], None],
) -> None:
    if balance < 0:
        send(f"balance is negative: {balance}")

@pytest.mark.parametrize("balance", [0, 50])
def test_mock_not_called(balance: float) -> None:
    send = Mock()
    notify_low_balance(balance, send)
    send.assert_not_called()

@pytest.mark.parametrize("balance", [0, 50])
def test_stub_not_called(balance: float) -> None:
    sent: list[str] = []
    def send(message: str) -> None:
        sent.append(message)
    notify_low_balance(balance, send)
    assert sent == []
