# classic_thermometer_demo.py
from classic_observer import Subject
from classic_thermometer import Thermometer

class Display:
    def update(
        self, subject: Subject[float], arg: float
    ) -> None:
        print(f"display: {arg}C")

t = Thermometer(20.0)
t.attach(Display())
t.set_celsius(25)
#: display: 25C
