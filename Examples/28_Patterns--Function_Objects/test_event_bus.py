# test_event_bus.py
from event_bus import Closed, Deposit, EventBus, Withdraw

def test_every_handler_for_the_type_is_called() -> None:
    seen: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit,
                  lambda e: seen.append(f"a{e.amount}"))
    bus.subscribe(Deposit,
                  lambda e: seen.append(f"b{e.amount}"))
    bus.publish(Deposit(5))
    assert seen == ["a5", "b5"]

def test_handler_receives_only_its_event_type() -> None:
    seen: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit,
                  lambda e: seen.append("deposit"))
    bus.subscribe(Withdraw,
                  lambda e: seen.append("withdraw"))
    bus.publish(Withdraw(1))
    assert seen == ["withdraw"]

def test_unhandled_event_raises_no_exception() -> None:
    bus = EventBus()
    bus.publish(Closed("done"))

def test_unhandled_event_leaves_no_stray_entry() -> None:
    bus = EventBus()
    bus.publish(Closed("done"))
    assert Closed not in bus._handlers
