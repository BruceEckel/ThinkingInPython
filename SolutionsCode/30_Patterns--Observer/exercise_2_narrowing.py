# exercise_2_narrowing.py
from typing import Protocol

class Observer[T](Protocol):
    def update(
        self, subject: Subject[T], arg: T
    ) -> None: ...

class Subject[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def attach(self, observer: Observer[T]) -> None:
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
        self, subject: Subject[float], arg: float
    ) -> None:
        assert isinstance(subject, Thermometer)
        print(f"display: {subject.celsius}C")

t = Thermometer(20.0)
t.attach(Display())
t.set_celsius(25)
#: display: 25C
