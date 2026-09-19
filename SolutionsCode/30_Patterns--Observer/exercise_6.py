# exercise_6.py
from collections.abc import Callable
from typing import overload

type Observer[T] = Callable[[T], None]

class Notifying[T]:
    def __set_name__(
        self, owner: type, name: str
    ) -> None:
        self.storage = f"_{name}"
        self.observers = f"_observers_{name}"

    @overload
    def __get__(self, obj: None,
                owner: type) -> Notifying[T]: ...
    @overload
    def __get__(self, obj: object,
                owner: type) -> T: ...
    def __get__(self, obj: object | None,
                owner: type) -> T | Notifying[T]:
        if obj is None:
            return self  # Thermometer.celsius
        return getattr(obj, self.storage)

    def __set__(self, obj: object, value: T) -> None:
        setattr(obj, self.storage, value)
        for observer in getattr(obj, self.observers, ()):
            observer(value)

    def subscribe(self, obj: object,
                  observer: Observer[T]) -> None:
        obj.__dict__.setdefault(
            self.observers, []).append(observer)

class Thermometer:
    celsius = Notifying[float]()
    humidity = Notifying[float]()

    def __init__(self, celsius: float,
                 humidity: float) -> None:
        self.celsius = celsius
        self.humidity = humidity

t = Thermometer(20.0, 0.4)
readings: list[float] = []
humidities: list[float] = []
Thermometer.celsius.subscribe(t, readings.append)
Thermometer.humidity.subscribe(t, humidities.append)
t.celsius = 25.0
t.humidity = 0.5
t.celsius = 150.0
print(readings, humidities)
#: [25.0, 150.0] [0.5]
print(t.celsius, t.humidity)
#: 150.0 0.5
