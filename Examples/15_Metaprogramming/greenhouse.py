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

def create_mc(description: str) -> None:
    "Create subclass using the 'type' metaclass."
    class_name = "".join(x.capitalize() for x in description.split())
    def init(self, time: float) -> None:
        Event.__init__(self, description + " [mc]", time)
    globals()[class_name] = type(
        class_name, (Event,), {"__init__": init})

def create_exec(description: str) -> None:
    "Create subclass by exec-ing a string."
    class_name = "".join(x.capitalize() for x in description.split())
    klass = f"""
class {class_name}(Event):
    def __init__(self, time: float) -> None:
        Event.__init__(self, "{description} [exec]", time)
"""
    exec(klass, globals())

if __name__ == "__main__":
    descriptions = ["Light on", "Light off", "Water on", "Water off",
                    "Thermostat night", "Thermostat day", "Ring bell"]
    initializations = "ThermostatNight(5.00); LightOff(2.00); \
        WaterOn(3.30); WaterOff(4.45); LightOn(1.00); \
        RingBell(7.00); ThermostatDay(6.00)"
    [create_mc(dsc) for dsc in descriptions]
    exec(initializations, globals())
    [create_exec(dsc) for dsc in descriptions]
    exec(initializations, globals())
    Event.run_events()
## 1.00: Light on [mc]
## 1.00: Light on [exec]
## 2.00: Light off [mc]
## 2.00: Light off [exec]
## 3.30: Water on [mc]
## 3.30: Water on [exec]
## 4.45: Water off [mc]
## 4.45: Water off [exec]
## 5.00: Thermostat night [mc]
## 5.00: Thermostat night [exec]
## 6.00: Thermostat day [mc]
## 6.00: Thermostat day [exec]
## 7.00: Ring bell [mc]
## 7.00: Ring bell [exec]
