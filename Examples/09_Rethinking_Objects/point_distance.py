# point_distance.py
# A method bound to the class, versus a plain function. The function
# reads the same and computes the same. The class does not need to
# own it.
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:  # As a method.
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)


def distance(a: Point, b: Point) -> float:  # As a free function.
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


if __name__ == "__main__":
    p1, p2 = Point(3, 0), Point(0, 4)  # A 3-4-5 right triangle.
    print(p1.distance_to(p2))
    print(distance(p1, p2))
