# broadcasting_thermometer.py
from broadcasting import Broadcasting

class Thermometer(Broadcasting[float]):
    celsius: float

thermometer = Thermometer(100)

@thermometer.respond
def display(celsius: float) -> None:
    print(f"display: {celsius}C")

@thermometer.respond
def alarm(celsius: float) -> None:
    print(f"alarm: {celsius > 100}")

thermometer.celsius = 90
#: display: 90C
#: alarm: False
thermometer.celsius = 150
#: display: 150C
#: alarm: True
thermometer.disconnect(alarm)
thermometer.celsius = 200
#: display: 200C
