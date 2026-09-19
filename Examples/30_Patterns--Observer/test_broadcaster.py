# test_broadcaster.py
import pytest
from broadcaster import Broadcaster, Thermometer

def test_announce_calls_every_subscriber() -> None:
    received: list[tuple[str, object]] = []
    source = Broadcaster[int]()
    source.subscribe(lambda d: received.append(("a", d)))
    source.subscribe(lambda d: received.append(("b", d)))
    source.announce(42)
    assert received == [("a", 42), ("b", 42)]

def test_no_subscribers_is_a_noop() -> None:
    # Must not raise anything
    Broadcaster[str]().announce("anything")

def test_unsubscribe_stops_delivery() -> None:
    received: list[object] = []
    source = Broadcaster[object]()
    # A bound method: equal, not identical
    record = received.append
    source.subscribe(record)
    source.announce(1)
    source.unsubscribe(record)
    source.announce(2)
    assert received == [1]

def test_subscribing_twice_notifies_twice() -> None:
    received: list[object] = []
    source = Broadcaster[object]()
    record = received.append
    source.subscribe(record)
    source.subscribe(record)
    source.announce(1)
    assert received == [1, 1]
    source.unsubscribe(record)  # Removes one of the two
    source.announce(2)
    assert received == [1, 1, 2]

def test_unsubscribe_without_subscribe_raises() -> None:
    source = Broadcaster[object]()
    with pytest.raises(ValueError):
        source.unsubscribe(print)

def test_thermometer_pushes_new_value_on_set() -> None:
    readings: list[float] = []
    t = Thermometer(20.0)
    assert t.celsius == 20.0  # The starting reading
    t.subscribe(readings.append)
    t.celsius = 25.0
    t.celsius = 150.0
    assert readings == [25.0, 150.0]
    assert t.celsius == 150.0

def test_late_subscriber_misses_earlier_changes() -> None:
    readings: list[float] = []
    t = Thermometer(0.0)
    t.celsius = 10.0  # No subscriber yet
    t.subscribe(readings.append)
    t.celsius = 20.0
    assert readings == [20.0]
