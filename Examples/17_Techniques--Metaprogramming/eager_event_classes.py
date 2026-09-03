# eager_event_classes.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final, cast

@dataclass
class Event:
    action: str
    hour: int
    minute: int

type EventMaker = Callable[[int, int], Event]
NAMES: Final[tuple[str, ...]] = (
    "ThermostatDay", "ThermostatNight", "LightOn",
    "LightOff", "WaterOn", "WaterOff", "RingBell",
)

def make(name: str) -> EventMaker:
    def init(self: Event, hour: int, minute: int) -> None:
        Event.__init__(self, name, hour, minute)
    new_cls = type(name, (Event,), {"__init__": init})
    return cast(EventMaker, new_cls)

makers = {name: make(name) for name in NAMES}
print(len(makers))
#: 7
light = makers["LightOn"](1, 0)
water = makers["WaterOff"](2, 0)
print(light)
#: LightOn(action='LightOn', hour=1, minute=0)
print(isinstance(light, Event))
#: True
print(type(light) is type(water))
#: False
