# Jython/GreenHouseLanguage.py

class Event:
    events = [] # static
    def __init__(self, action, time):
        self.action = action
        self.time = time
        Event.events.append(self)
    # Used by sort(). This will cause
    # comparisons to be based only on time:
    def __cmp__ (self, other):
        if self.time < other.time: return -1
        if self.time > other.time: return 1
        return 0
    def run(self):
        print("%.2f: %s" % (self.time, self.action))

class LightOn(Event):
    def __init__(self, time):
        Event.__init__(self, "Light on", time)

class LightOff(Event):
    def __init__(self, time):
        Event.__init__(self, "Light off", time)

class WaterOn(Event):
    def __init__(self, time):
        Event.__init__(self, "Water on", time)

class WaterOff(Event):
    def __init__(self, time):
        Event.__init__(self, "Water off", time)

class ThermostatNight(Event):
    def __init__(self, time):
        Event.__init__(self,"Thermostat night", time)

class ThermostatDay(Event):
    def __init__(self, time):
        Event.__init__(self, "Thermostat day", time)

class Bell(Event):
    def __init__(self, time):
        Event.__init__(self, "Ring bell", time)

def run():
    Event.events.sort();
    for e in Event.events:
        e.run()

# To test, this will be run when you say:
# python GreenHouseLanguage.py
if __name__ == "__main__":
    ThermostatNight(5.00)
    LightOff(2.00)
    WaterOn(3.30)
    WaterOff(4.45)
    LightOn(1.00)
    ThermostatDay(6.00)
    Bell(7.00)
    run()