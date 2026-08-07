# exercise_6.py
from chladni import Plate, amplitude

print(amplitude(0.31, 0.79, (2, 2)))
#: 0.0
plate = Plate(grains=2000, mode=(2, 2), seed=42)
before = [(g.x, g.y) for g in plate.grains]
for _ in range(1200):
    plate.step()
after = [(g.x, g.y) for g in plate.grains]
print(f"agitation {plate.agitation():.3f}, moved {before != after}")
#: agitation 0.000, moved False
print(amplitude(0.37, 0.37, (1, 2)))
#: 0.0
