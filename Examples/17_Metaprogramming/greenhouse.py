# greenhouse.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, cast

type EventMaker = Callable[[float], Event]
NOT_CREATED = cast(EventMaker, sentinel("NOT_CREATED"))

@dataclass
class Event:
    events: ClassVar[list[Event]] = []  # Registry of all Events
    subclasses: ClassVar[dict[str, EventMaker]] = {
        name: NOT_CREATED  # Dict key-value pair
        for name in (
            "ThermostatDay", "ThermostatNight",
            "LightOn", "LightOff",
            "WaterOn", "WaterOff",
            "RingBell",
        )
    }
    action: str
    time: float

    def __post_init__(self) -> None:
        Event.events.append(self)

    @staticmethod
    def run_events() -> None:
        for e in sorted(Event.events, key=lambda e: e.time):
            print(f"{e.time:.2f}: {e.action}")

    @classmethod
    def _create(cls, class_name: str) -> None:
        if class_name not in cls.subclasses:
            raise ValueError(f"Unknown event class: {class_name!r}")
        def init(self: Event, time: float) -> None:
            Event.__init__(self, class_name, time)
        new_cls = type(class_name, (Event,), {"__init__": init})
        cls.subclasses[class_name] = cast(EventMaker, new_cls)

    @classmethod
    def initialize(cls) -> None:
        for class_name in cls.subclasses:
            cls._create(class_name)

    @classmethod
    def instantiate(cls, init: str) -> None:
        class_name, rest = init.split("(", 1)
        if class_name not in cls.subclasses:
            raise ValueError(f"Unknown event class: {class_name!r}")
        time = float(rest.rstrip(")"))
        cls.subclasses[class_name](time)

if __name__ == "__main__":
    initializations = [
        "ThermostatNight(5.00)",
        "LightOff(2.00)",
        "WaterOn(3.30)",
        "WaterOff(4.45)",
        "LightOn(1.00)",
        "RingBell(7.00)",
        "ThermostatDay(6.00)",
    ]
    Event.initialize()
    for init in initializations:
        Event.instantiate(init)
    Event.run_events()
#: 1.00: LightOn
#: 2.00: LightOff
#: 3.30: WaterOn
#: 4.45: WaterOff
#: 5.00: ThermostatNight
#: 6.00: ThermostatDay
#: 7.00: RingBell
