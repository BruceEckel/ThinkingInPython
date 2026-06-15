# observers.py
# An observer is just a callable; an observable is a list of them.
# No Observer interface and no Observable base class to inherit.
from collections.abc import Callable
from typing import Any


class Observable:
    def __init__(self) -> None:
        self._observers: list[Callable[[Any], None]] = []

    def subscribe(self, observer: Callable[[Any], None]) -> None:
        self._observers.append(observer)

    def notify(self, data: Any) -> None:
        for observer in self._observers:
            observer(data)


class Thermometer(Observable):
    def __init__(self) -> None:
        super().__init__()
        self._celsius = 0.0

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)   # state changed; tell the observers


thermo = Thermometer()
thermo.subscribe(lambda c: print(f"display: {c}C"))
thermo.subscribe(lambda c: print("alarm!" if c > 100 else "ok"))
thermo.celsius = 25
thermo.celsius = 150
