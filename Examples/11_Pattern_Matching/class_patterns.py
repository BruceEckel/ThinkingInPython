# class_patterns.py
from point import Point

def locate(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "The origin"
        case Point(0, y):
            return f"On the y-axis at y={y}"
        case Point(x, 0):
            return f"On the x-axis at x={x}"
        case Point(x, y):
            return f"At ({x}, {y})"

print(locate(Point(0, 0)))
#: The origin
print(locate(Point(0, 5)))
#: On the y-axis at y=5
print(locate(Point(3, 0)))
#: On the x-axis at x=3
print(locate(Point(3, 4)))
#: At (3, 4)
