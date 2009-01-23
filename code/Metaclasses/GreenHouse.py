# Metaclasses/GreenHouse.py

class Event(object):
    events = [] # static

    def __init__(self, action, time):
        self.action = action
        self.time = time
        Event.events.append(self)

    def __cmp__ (self, other):
        "So sort() will compare only on time."
        return cmp(self.time, other.time)

    def run(self):
        print("%.2f: %s" % (self.time, self.action))

    @staticmethod
    def run_events():
        Event.events.sort();
        for e in Event.events:
            e.run()

def create_mc(description):
    "Create subclass using the 'type' metaclass"
    class_name = "".join(x.capitalize() for x in description.split())
    def __init__(self, time):
        Event.__init__(self, description + " [mc]", time)
    globals()[class_name] = \
        type(class_name, (Event,), dict(__init__ = __init__))

def create_exec(description):
    "Create subclass by exec-ing a string"
    class_name = "".join(x.capitalize() for x in description.split())
    klass = """
class %s(Event):
    def __init__(self, time):
        Event.__init__(self, "%s [exec]", time)
""" % (class_name, description)
    exec klass in globals()

if __name__ == "__main__":
    descriptions = ["Light on", "Light off", "Water on", "Water off", 
                    "Thermostat night", "Thermostat day", "Ring bell"]
    initializations = "ThermostatNight(5.00); LightOff(2.00); \
        WaterOn(3.30); WaterOff(4.45); LightOn(1.00); \
        RingBell(7.00); ThermostatDay(6.00)"
    [create_mc(dsc) for dsc in descriptions]
    exec initializations in globals()
    [create_exec(dsc) for dsc in descriptions]
    exec initializations in globals()
    Event.run_events()

""" Output:
1.00: Light on [mc]
1.00: Light on [exec]
2.00: Light off [mc]
2.00: Light off [exec]
3.30: Water on [mc]
3.30: Water on [exec]
4.45: Water off [mc]
4.45: Water off [exec]
5.00: Thermostat night [mc]
5.00: Thermostat night [exec]
6.00: Thermostat day [mc]
6.00: Thermostat day [exec]
7.00: Ring bell [mc]
7.00: Ring bell [exec]
"""
