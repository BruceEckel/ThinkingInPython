# classic_observer.py
from typing import Protocol

class Observer[T](Protocol):
    def update(
        self, observable: Observable[T], arg: T
    ) -> None: ...

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def attach(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer[T]) -> None:
        self._observers.remove(observer)

    def notify(self, arg: T) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Display:
    def update(
        self, observable: Observable[float], arg: float
    ) -> None:
        print(f"display: {arg}C")

class Thermometer(Observable[float]):
    def set_celsius(self, value: float) -> None:
        self.notify(value)

t = Thermometer()
t.attach(Display())
t.set_celsius(25)
#: display: 25C
