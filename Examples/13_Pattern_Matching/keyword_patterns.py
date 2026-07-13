# keyword_patterns.py
from point import Point

def describe(p: Point) -> str:
    match p:
        case Point(x=0):
            return "Somewhere on the y-axis"
        case Point(y=0):
            return "Somewhere on the x-axis"
        case Point(x=x, y=y) if x == y:
            return f"On the diagonal at {x}"
        case Point():
            return "Just some point"

print(describe(Point(0, 5)))
#: Somewhere on the y-axis
print(describe(Point(3, 0)))
#: Somewhere on the x-axis
print(describe(Point(2, 2)))
#: On the diagonal at 2
print(describe(Point(3, 4)))
#: Just some point
