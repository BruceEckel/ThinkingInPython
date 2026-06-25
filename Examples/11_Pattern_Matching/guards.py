# guards.py
from point import Point

def quadrant(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "Origin"
        case Point(x, y) if x > 0 and y > 0:
            return "First quadrant"
        case Point(x, y) if x < 0 and y > 0:
            return "Second quadrant"
        case _:
            return "Somewhere else"

print(quadrant(Point(0, 0)))
## Origin
print(quadrant(Point(3, 4)))
## First quadrant
print(quadrant(Point(-3, 4)))
## Second quadrant
print(quadrant(Point(-1, -1)))
## Somewhere else
