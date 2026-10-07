# broadcasting_demo.py
from broadcasting import Broadcasting

class Thermometer(Broadcasting[float]):
    celsius: float

thermometer = Thermometer(100)

@thermometer.respond
def report(celsius: float) -> None:
    print(f"report: {celsius}C")

@thermometer.respond
def alarm(celsius: float) -> None:
    print("alarm!" if celsius > 100 else "ok")

thermometer.celsius = 90
#: report: 90C
#: ok
thermometer.celsius = 150
#: report: 150C
#: alarm!
