# events.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

@dataclass
class Event:
    action: str
    hour: int
    minute: int

type EventMaker = Callable[[int, int], Event]
NAMES: Final[frozenset[str]] = frozenset({
    "ThermostatDay", "ThermostatNight", "LightOn",
    "LightOff", "WaterOn", "WaterOff", "RingBell",
})

def make(name: str) -> EventMaker:
    def init(self: Event, hour: int, minute: int) -> None:
        Event.__init__(self, name, hour, minute)
    new_cls = type(name, (Event,), {"__init__": init})
    return new_cls
