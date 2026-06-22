# class_patterns.py
# A class pattern matches the type and binds attributes. A data class
# supports positional matching out of the box.
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def locate(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "the origin"
        case Point(0, y):
            return f"on the y-axis at y={y}"
        case Point(x, 0):
            return f"on the x-axis at x={x}"
        case Point(x, y):
            return f"at ({x}, {y})"

print(locate(Point(0, 0)))
print(locate(Point(0, 5)))
print(locate(Point(3, 0)))
print(locate(Point(3, 4)))
