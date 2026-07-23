# point_distance.py
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:  # Method
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

def distance(a: Point, b: Point) -> float:  # Free function
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

if __name__ == "__main__":
    p1, p2 = Point(3, 0), Point(0, 4)  # A 3-4-5 right triangle
    print(p1.distance_to(p2))
    print(Point.distance_to(p1, p2))  # The method, as a function
    print(distance(p1, p2))
#: 5.0
#: 5.0
#: 5.0
