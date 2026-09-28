# greenhouse_demo.py
from pathlib import Path
from greenhouse import Event

Event.load_schedule(Path("schedule.txt"))
Event.run_events()
#: Creating LightOff
#: Creating LightOn
#: Creating RingBell
#: 1:00: LightOn
#: 2:00: LightOff
#: * 7:00: RingBell
#: 8:00: LightOn
