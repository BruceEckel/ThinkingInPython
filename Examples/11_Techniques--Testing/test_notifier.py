# test_notifier.py
from unittest.mock import Mock
import notifier

def test_negative_balance_sends_message() -> None:
    send = Mock()
    notifier.notify_low_balance(-5, send)
    send.assert_called_once_with(
        "balance is negative: -5")
