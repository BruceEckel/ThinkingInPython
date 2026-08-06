# exercise_5_signs.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def sign(n: int) -> int:
    return (n > 0) - (n < 0)

def quadrant(p: Point) -> str:
    match sign(p.x), sign(p.y):
        case 0, 0:
            return "Origin"
        case 1, 1:
            return "First quadrant"
        case -1, 1:
            return "Second quadrant"
        case -1, -1:
            return "Third quadrant"
        case 1, -1:
            return "Fourth quadrant"
        case (0, _) | (_, 0):
            return "On an axis"
        case _:
            return "unreachable"

print(quadrant(Point(-3, -4)), quadrant(Point(3, -4)))
#: Third quadrant Fourth quadrant
print(quadrant(Point(0, 7)))
#: On an axis
