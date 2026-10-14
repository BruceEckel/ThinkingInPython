# greenhouse.py
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

class EventMakers(dict[str, EventMaker]):
    def __missing__(self, name: str) -> EventMaker:
        if name not in NAMES:
            raise KeyError(f"Unknown event class: {name!r}")
        print(f"Creating {name}")
        # Local function to pass to type constructor:
        def init(self: Event,
                 hour: int, minute: int) -> None:
            Event.__init__(self, name, hour, minute)
        new_cls = type(name, (Event,), {"__init__": init})
        self[name] = new_cls
        return new_cls

    def built(self) -> str:
        return (f"{len(self)} of {len(NAMES)}"
                " event classes built")
