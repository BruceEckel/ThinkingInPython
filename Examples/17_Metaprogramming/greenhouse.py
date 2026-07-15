# greenhouse.py
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Event:
    events: ClassVar[list[Event]] = []  # Registry of all Events
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

def create_via_metaclass(class_name: str) -> None:
    # A local function, to include in the generated class:
    def init(self, time: float) -> None:
        Event.__init__(self, class_name + " [mc]", time)
    globals()[class_name] = type(
        class_name, (Event,), {"__init__": init})

def create_via_exec(class_name: str) -> None:
    klass = f"""
class {class_name}(Event):
    def __init__(self, time: float) -> None:
        Event.__init__(self, "{class_name} [exec]", time)
"""
    exec(klass, globals())

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
    class_names = [init.split("(")[0] for init in initializations]
    for class_name in class_names:
        create_via_metaclass(class_name)
    for init in initializations:
        exec(init, globals())
    for class_name in class_names:
        create_via_exec(class_name)
    for init in initializations:
        exec(init, globals())
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
