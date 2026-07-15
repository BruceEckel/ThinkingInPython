# greenhouse.py
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, cast

type EventMaker = Callable[[int, int], Event]
NOT_CREATED = cast(EventMaker, sentinel("NOT_CREATED"))

@dataclass
class Event:
    events: ClassVar[list[Event]] = []  # Registry of all Events
    event_makers: ClassVar[dict[str, EventMaker]] = {
        name: NOT_CREATED  # Dict key-value pair
        for name in (
            "ThermostatDay", "ThermostatNight",
            "LightOn", "LightOff",
            "WaterOn", "WaterOff",
            "RingBell",
        )
    }
    action: str
    hour: int
    minute: int

    def __post_init__(self) -> None:
        Event.events.append(self)

    @staticmethod
    def run_events() -> None:
        for e in sorted(
                Event.events, key=lambda e: (e.hour, e.minute)):
            print(f"{e.hour}:{e.minute:02d}: {e.action}")

    @classmethod
    def _make_class(cls, class_name: str) -> None:
        if class_name not in cls.event_makers:
            raise ValueError(f"Unknown event class: {class_name!r}")
        if cls.event_makers[class_name] is not NOT_CREATED:
            return
        print(f"Creating {class_name}")
        def init(self: Event, hour: int, minute: int) -> None:
            Event.__init__(self, class_name, hour, minute)
        new_cls = type(class_name, (Event,), {"__init__": init})
        cls.event_makers[class_name] = cast(EventMaker, new_cls)

    @classmethod
    def add_event(cls, event: str) -> None:
        class_name, hour, minute = (event.replace(":", " ").split())
        cls._make_class(class_name)
        cls.event_makers[class_name](int(hour), int(minute))

if __name__ == "__main__":
    schedule = [
        line for line in Path("schedule.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    for event in schedule:
        Event.add_event(event)
    Event.run_events()
#: Creating ThermostatNight
#: Creating LightOff
#: Creating WaterOn
#: Creating WaterOff
#: Creating LightOn
#: Creating RingBell
#: Creating ThermostatDay
#: 1:00: LightOn
#: 2:00: LightOff
#: 3:30: WaterOn
#: 4:45: WaterOff
#: 5:00: ThermostatNight
#: 6:00: ThermostatDay
#: 7:00: RingBell
#: 8:00: LightOn
