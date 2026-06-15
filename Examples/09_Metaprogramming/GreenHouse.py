# greenhouse.py

class Event:
    events: list["Event"] = [] # static

    def __init__(self, action: str, time: float) -> None:
        self.action = action
        self.time = time
        Event.events.append(self)

    def run(self) -> None:
        print("%.2f: %s" % (self.time, self.action))

    @staticmethod
    def run_events() -> None:
        for e in sorted(Event.events, key=lambda e: e.time):
            e.run()

def create_mc(description: str) -> None:
    "Create subclass using the 'type' metaclass"
    class_name = "".join(x.capitalize() for x in description.split())
    def __init__(self, time):
        Event.__init__(self, description + " [mc]", time)
    globals()[class_name] = \
        type(class_name, (Event,), dict(__init__ = __init__))

def create_exec(description: str) -> None:
    "Create subclass by exec-ing a string"
    class_name = "".join(x.capitalize() for x in description.split())
    klass = """
class %s(Event):
    def __init__(self, time):
        Event.__init__(self, "%s [exec]", time)
""" % (class_name, description)
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
