# exercise_8.py
from chladni import Plate

for kick in (0.005, 0.05, 0.5):
    plate = Plate(grains=2000, mode=(2, 3), seed=42)
    steps = 0
    readings = []
    for target in (0, 100, 400, 1200):
        for _ in range(target - steps):
            plate.step(kick=kick)
        steps = target
        readings.append(f"{plate.agitation():.2f}")
    print(f"kick {kick:<5}: {' '.join(readings)}")
#: kick 0.005: 0.58 0.56 0.49 0.38
#: kick 0.05 : 0.58 0.07 0.00 0.00
#: kick 0.5  : 0.58 0.11 0.01 0.00
