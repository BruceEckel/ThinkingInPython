# greenhouse.py
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, cast

type EventMaker = Callable[[int, int], Event]
NOT_CREATED = sentinel("NOT_CREATED")

class EventMakers(dict[str, EventMaker | NOT_CREATED]):
    def __getitem__(self, class_name: str) -> EventMaker:
        if class_name not in self:
            raise KeyError(
                f"Unknown event class: {class_name!r}")
        maker = super().__getitem__(class_name)
        if maker is NOT_CREATED:
            print(f"Creating {class_name}")
            # Local function to pass to type constructor:
            def init(self: Event,
                     hour: int, minute: int) -> None:
                Event.__init__(
                    self, class_name, hour, minute)
            new_cls = type(class_name, (Event,),
                           {"__init__": init})
            maker = cast(EventMaker, new_cls)
            self[class_name] = maker
        return maker

@dataclass
class Event:
    action: str
    hour: int
    minute: int
    # Registry of all Events
    events: ClassVar[list[Event]] = []
    _event_maker: ClassVar[EventMakers] = EventMakers({
        name : NOT_CREATED  # Dict key : value
        for name in (
            "ThermostatDay", "ThermostatNight",
            "LightOn", "LightOff",
            "WaterOn", "WaterOff",
            "RingBell",
        )
    })

    def __post_init__(self) -> None:
        Event.events.append(self)

    @staticmethod
    def load_schedule(path: Path) -> None:
        lines = [
            line for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
        for line in lines:
            class_name, hour, minute = (
                line.replace(":", " ").split())
            Event._event_maker[class_name](
                int(hour), int(minute))

    @staticmethod
    def run_events() -> None:
        for e in sorted(
                Event.events,
                key=lambda e: (e.hour, e.minute)):
            print(f"{e.hour}:{e.minute:02d}: {e.action}")

if __name__ == "__main__":
    Event.load_schedule(Path("schedule.txt"))
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
