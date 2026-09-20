# exercise_2_generic.py
from typing import Protocol, Self

class Observer[S, T](Protocol):
    def update(self, subject: S, arg: T) -> None: ...

class Subject[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[Self, T]] = []

    def attach(
        self, observer: Observer[Self, T]
    ) -> None:
        self._observers.append(observer)

    def notify(self, arg: T) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Thermometer(Subject[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    def set_celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)

class Display:
    def update(
        self, subject: Thermometer, arg: float
    ) -> None:
        print(f"display: {subject.celsius}C")

t = Thermometer(20.0)
t.attach(Display())
t.set_celsius(25)
#: display: 25C
