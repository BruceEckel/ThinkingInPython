# slots_dataclass.py
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)
#: Point(x=1, y=2)
print(Point.__slots__)
#: ('x', 'y')
