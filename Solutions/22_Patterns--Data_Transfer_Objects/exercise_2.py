# exercise_2.py
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

p = Point(1.0, 2.0, 3.0)
print(p)
#: Point(x=1.0, y=2.0, z=3.0)
p.x = 3.5
print(p == Point(3.5, 2.0, 3.0))
#: True
