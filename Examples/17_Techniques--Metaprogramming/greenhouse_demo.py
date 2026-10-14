# greenhouse_demo.py
from typing import Final, cast
from greenhouse import EventMakers

SCHEDULE: Final[tuple[tuple[str, int, int], ...]] = (
    ("LightOff", 2, 0),
    ("LightOn", 1, 0),
    ("RingBell", 7, 0),
    ("LightOn", 8, 0),
)
makers = EventMakers()
events = [makers[name](hour, minute)
          for name, hour, minute in SCHEDULE]
#: Creating LightOff
#: Creating LightOn
#: Creating RingBell
print(makers.built())
#: 3 of 7 event classes built
bell = cast(type, makers["RingBell"])
for event in sorted(
        events, key=lambda e: (e.hour, e.minute)):
    prefix = "* " if isinstance(event, bell) else ""
    print(f"{prefix}{event.hour}:{event.minute:02d}"
          f": {event.action}")
#: 1:00: LightOn
#: 2:00: LightOff
#: * 7:00: RingBell
#: 8:00: LightOn
