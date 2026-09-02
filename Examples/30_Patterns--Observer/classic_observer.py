# classic_observer.py
from abc import ABC, abstractmethod
from typing import override

class Observer(ABC):
    @abstractmethod
    def update(
        self, subject: Subject, arg: object
    ) -> None: ...

class Subject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, arg: object = None) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Display(Observer):
    @override
    def update(
        self, subject: Subject, arg: object
    ) -> None:
        print(f"display: {arg}C")

class Thermometer(Subject):
    def set_celsius(self, value: float) -> None:
        self.notify(value)

t = Thermometer()
t.attach(Display())
t.set_celsius(25)
#: display: 25C
