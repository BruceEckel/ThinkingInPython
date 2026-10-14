# thermometer_demo.py
from thermometer import Thermometer

def display(celsius: float) -> None:
    print(f"display: {celsius}C")

def alarm(celsius: float) -> None:
    print(f"alarm: {celsius > 100}")

t = Thermometer(20.0)
t.connect(display)
t.connect(alarm)
t.celsius = 25
#: display: 25C
#: alarm: False
t.celsius = 150
#: display: 150C
#: alarm: True
