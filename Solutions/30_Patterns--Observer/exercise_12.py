# exercise_12.py
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any, dataclass_transform

type Responder[T] = Callable[[str, T], None]

def published(name: str) -> property:
    def read(self: Any) -> Any:
        return self.__dict__[name]

    def write(self: Any, value: Any) -> None:
        self.__dict__[name] = value
        self.announce(name, value)

    return property(read, write)

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls) -> None:
        built = dataclass(eq=False)(cls)
        for field in fields(built):
            prop = published(field.name)
            setattr(cls, field.name, prop)

    @property
    def _responders(self) -> list[Responder[T]]:
        return self.__dict__.setdefault("_responders", [])

    def respond(self, fn: Responder[T]) -> Responder[T]:
        self._responders.append(fn)
        return fn

    def disconnect(self, fn: Responder[T]) -> None:
        self._responders.remove(fn)

    def announce(self, name: str, data: T) -> None:
        for responder in list(self._responders):
            responder(name, data)

class Station(Broadcasting[float]):
    celsius: float
    humidity: float

station = Station(20.0, 0.4)
calls: list[str] = []

@station.respond
def report(name: str, value: float) -> None:
    calls.append(name)
    if name == "celsius":
        print(f"report: {value}C")

station.celsius = 25.0
#: report: 25.0C
station.humidity = 0.5
print(calls)
#: ['celsius', 'humidity']
