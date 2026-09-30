# thermometer_demo.py
from thermometer import Thermometer

t = Thermometer(20.0)
t.connect(lambda c: print(f"display: {c}C"))
t.connect(lambda c: print("alarm!" if c > 100 else "ok"))
t.celsius = 25
#: display: 25C
#: ok
t.celsius = 150
#: display: 150C
#: alarm!
