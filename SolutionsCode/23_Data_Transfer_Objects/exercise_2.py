# exercise_2.py
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

print(Point(1.0, 2.0, 3.0))
#: Point(x=1.0, y=2.0, z=3.0)
