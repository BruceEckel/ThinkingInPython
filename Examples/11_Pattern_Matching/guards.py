# guards.py
# A guard adds a condition to a case.
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


def quadrant(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "origin"
        case Point(x, y) if x > 0 and y > 0:
            return "first quadrant"
        case Point(x, y) if x < 0 and y > 0:
            return "second quadrant"
        case _:
            return "somewhere else"


print(quadrant(Point(0, 0)))
print(quadrant(Point(3, 4)))
print(quadrant(Point(-3, 4)))
print(quadrant(Point(-1, -1)))
