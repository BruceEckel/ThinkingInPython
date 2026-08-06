# exercise_5.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def quadrant(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "Origin"
        case Point(x, y) if x > 0 and y > 0:
            return "First quadrant"
        case Point(x, y) if x < 0 and y > 0:
            return "Second quadrant"
        case Point(x, y) if x < 0 and y < 0:
            return "Third quadrant"
        case Point(x, y) if x > 0 and y < 0:
            return "Fourth quadrant"
        case _:
            return "On an axis"

print(quadrant(Point(-3, -4)), quadrant(Point(3, -4)))
#: Third quadrant Fourth quadrant
print(quadrant(Point(0, 7)))
#: On an axis
