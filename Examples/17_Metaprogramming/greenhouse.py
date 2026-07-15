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
        name: NOT_CREATED  # The dict pair
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

    def run(self) -> None:
        print(f"{self.time:.2f}: {self.action}")

    @staticmethod
    def run_events() -> None:
        for e in sorted(Event.events, key=lambda e: e.time):
            e.run()

    @classmethod
    def _create_via_metaclass(cls, class_name: str) -> None:
        if class_name not in cls.subclasses:
            raise ValueError(f"Unknown event class: {class_name!r}")
        def init(self: Event, time: float) -> None:
            Event.__init__(self, class_name + " [mc]", time)
        new_cls = type(class_name, (Event,), {"__init__": init})
        cls.subclasses[class_name] = cast(EventMaker, new_cls)

    @classmethod
    def _create_via_exec(cls, class_name: str) -> None:
        if class_name not in cls.subclasses:
            raise ValueError(f"Unknown event class: {class_name!r}")
        namespace: dict[str, type[Event]] = {"Event": Event}
        klass = f"""
class {class_name}(Event):
    def __init__(self, time: float) -> None:
        Event.__init__(self, "{class_name} [exec]", time)
"""
        exec(klass, namespace)
        cls.subclasses[class_name] = cast(
            EventMaker, namespace[class_name])

    @classmethod
    def initialize_via_metaclass(cls) -> None:
        for class_name in cls.subclasses:
            cls._create_via_metaclass(class_name)

    @classmethod
    def initialize_via_exec(cls) -> None:
        for class_name in cls.subclasses:
            cls._create_via_exec(class_name)

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
    Event.initialize_via_metaclass()
    for init in initializations:
        Event.instantiate(init)
    Event.initialize_via_exec()
    for init in initializations:
        Event.instantiate(init)
    Event.run_events()
#: 1.00: LightOn [mc]
#: 1.00: LightOn [exec]
#: 2.00: LightOff [mc]
#: 2.00: LightOff [exec]
#: 3.30: WaterOn [mc]
#: 3.30: WaterOn [exec]
#: 4.45: WaterOff [mc]
#: 4.45: WaterOff [exec]
#: 5.00: ThermostatNight [mc]
#: 5.00: ThermostatNight [exec]
#: 6.00: ThermostatDay [mc]
#: 6.00: ThermostatDay [exec]
#: 7.00: RingBell [mc]
#: 7.00: RingBell [exec]
