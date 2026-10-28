# events.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

type Hour = int
type Minute = int

@dataclass
class Event:
    action: str
    hour: Hour
    minute: Minute

type EventMaker = Callable[[Hour, Minute], Event]
NAMES: Final[frozenset[str]] = frozenset({
    "ThermostatDay", "ThermostatNight", "LightOn",
    "LightOff", "WaterOn", "WaterOff", "RingBell",
})

def make(name: str) -> EventMaker:
    def init(self: Event, hour: Hour,
             minute: Minute) -> None:
        Event.__init__(self, name, hour, minute)
    new_cls = type(name, (Event,), {"__init__": init})
    return new_cls
