# eager_event_classes.py
from events import NAMES, Event, make

makers = {name: make(name) for name in NAMES}
print(len(makers))
#: 7
light = makers["LightOn"](1, 0)
water = makers["WaterOff"](2, 0)
print(light)
#: LightOn(action='LightOn', hour=1, minute=0)
print(isinstance(light, Event))
#: True
print(type(light) is type(water))
#: False
