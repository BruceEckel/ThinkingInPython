# test_tagged_bus.py
import pytest
from tagged_bus import Deposit, EventBus, Withdraw, handler

def test_handler_receives_its_event() -> None:
    seen: list[int] = []
    @handler
    class Record:
        def __call__(self, event: Deposit) -> None:
            seen.append(event.amount)
    bus = EventBus()
    bus.subscribe(Record())
    bus.publish(Deposit(5))
    bus.publish(Withdraw(1))
    assert seen == [5]

def test_publish_rejects_a_non_event() -> None:
    with pytest.raises(TypeError, match="not an @event"):
        EventBus().publish("Deposit")

def test_subscribe_rejects_an_undecorated_class() -> None:
    class Plain:
        def __call__(self, event: Deposit) -> None: ...
    with pytest.raises(TypeError, match="not a @handler"):
        EventBus().subscribe(Plain())

def test_handler_needs_a_call_on_an_event() -> None:
    with pytest.raises(TypeError, match="has no __call__"):
        @handler
        class NoCall:
            x: int
    with pytest.raises(TypeError, match="not an @event"):
        @handler
        class WrongEvent:
            def __call__(self, event: int) -> None: ...
