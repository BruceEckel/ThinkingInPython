# exercise_1.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def classify(value):
    match value:
        case []:
            return "empty list"
        case [_]:
            return "singleton"
        case [_, *_]:
            return "longer list"
        case Point():
            return "point"
        case _:
            return "other"

print(classify([]))
#: empty list
print(classify([1]))
#: singleton
print(classify([1, 2, 3]))
#: longer list
print(classify(Point(1, 2)))
#: point
print(classify("hi"))
#: other
