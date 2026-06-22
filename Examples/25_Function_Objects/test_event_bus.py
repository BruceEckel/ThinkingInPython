# test_event_bus.py
from event_bus import Closed, Deposit, EventBus, Withdraw

def test_every_handler_for_the_type_is_called() -> None:
    seen: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit, lambda e: seen.append(f"a{e.amount}"))
    bus.subscribe(Deposit, lambda e: seen.append(f"b{e.amount}"))
    bus.publish(Deposit(5))
    assert seen == ["a5", "b5"]

def test_only_the_matching_type_is_called() -> None:
    calls: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit, lambda e: calls.append("deposit"))
    bus.subscribe(Withdraw, lambda e: calls.append("withdraw"))
    bus.publish(Withdraw(1))
    assert calls == ["withdraw"]

def test_no_handler_is_a_noop() -> None:
    EventBus().publish(Closed("done"))  # Must not raise
