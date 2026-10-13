# greenhouse.py
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, cast

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

@dataclass
class Event:
    action: str
    hour: int
    minute: int
    # Registry of all Events
    events: ClassVar[list[Event]] = []
    _event_maker: ClassVar[EventMakers] = EventMakers()

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
        bell = cast(
            type, Event._event_maker["RingBell"])
        for e in sorted(
                Event.events,
                key=lambda e: (e.hour, e.minute)):
            prefix = "* " if isinstance(e, bell) else ""
            line = f"{e.hour}:{e.minute:02d}: {e.action}"
            print(prefix + line)
