# exercise_11.py
from collections.abc import Callable
from typing import Final

type Responder = Callable[[float], None]

RESPONDERS: Final[list[Responder]] = []

def responds(fn: Responder) -> Responder:
    RESPONDERS.append(fn)
    return fn

class Thermometer:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        for responder in RESPONDERS:
            responder(value)

@responds
def display(celsius: float) -> None:
    print(f"display: {celsius}C")

@responds
def alarm(celsius: float) -> None:
    if celsius > 100:
        print("alarm!")

room = Thermometer(20.0)
oven = Thermometer(180.0)
room.celsius = 21.0
#: display: 21.0C
oven.celsius = 200.0
#: display: 200.0C
#: alarm!
