# test_observers.py
from observers import Observable, Thermometer


def test_notify_calls_every_subscriber() -> None:
    received: list[tuple[str, object]] = []
    obs = Observable()
    obs.subscribe(lambda d: received.append(("a", d)))
    obs.subscribe(lambda d: received.append(("b", d)))
    obs.notify(42)
    assert received == [("a", 42), ("b", 42)]


def test_no_subscribers_is_a_noop() -> None:
    Observable().notify("anything")  # must not raise


def test_thermometer_pushes_new_value_on_set() -> None:
    readings: list[float] = []
    thermo = Thermometer()
    thermo.subscribe(readings.append)
    thermo.celsius = 25.0
    thermo.celsius = 150.0
    assert readings == [25.0, 150.0]
    assert thermo.celsius == 150.0


def test_late_subscriber_misses_earlier_changes() -> None:
    readings: list[float] = []
    thermo = Thermometer()
    thermo.celsius = 10.0  # no subscriber yet
    thermo.subscribe(readings.append)
    thermo.celsius = 20.0
    assert readings == [20.0]
