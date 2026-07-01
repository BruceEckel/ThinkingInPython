# thermometer.py
from observers import Thermometer

t = Thermometer()
t.subscribe(lambda c: print(f"display: {c}C"))
t.subscribe(lambda c: print("alarm!" if c > 100 else "ok"))
t.celsius = 25
#: display: 25C
#: ok
t.celsius = 150
#: display: 150C
#: alarm!
