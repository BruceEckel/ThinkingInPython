# classic_observer.py
from abc import ABC, abstractmethod
from typing import override

class Observer(ABC):
    @abstractmethod
    def update(self, source: Observable, arg: object) -> None: ...

class Observable:
    def __init__(self) -> None:
        self._observers: list[Observer] = []
        self._changed = False

    def add_observer(self, observer: Observer) -> None:
        self._observers.append(observer)

    def set_changed(self) -> None:
        self._changed = True

    def notify_observers(self, arg: object = None) -> None:
        if not self._changed:
            return
        for observer in list(self._observers):
            observer.update(self, arg)
        self._changed = False

class Display(Observer):
    @override
    def update(self, source: Observable, arg: object) -> None:
        print(f"display: {arg}C")

class Thermometer(Observable):
    def set_celsius(self, value: float) -> None:
        self.set_changed()
        self.notify_observers(value)

t = Thermometer()
t.add_observer(Display())
t.set_celsius(25)
#: display: 25C
