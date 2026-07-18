# observers.py
from collections.abc import Callable
from typing import Any

type Observer = Callable[[Any], None]

class Observable:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, data: Any) -> None:
        # Copy: observers may detach during notification
        for observer in list(self._observers):
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
        self.notify(value)  # State changed; tell the observers
