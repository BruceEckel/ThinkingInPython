# exercise_2.py
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

def distance(a: Point, b: Point) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

p1, p2 = Point(3, 0), Point(0, 4)
p3 = Point(6, 8)
print(distance(p1, p3))
#: 8.54400374531753
print(p1.distance_to(p3))
#: 8.54400374531753
