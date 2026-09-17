# exercise_5.py
import math
from typing import assert_never
from record import record

@record
class Rectangle:
    length: float
    width: float

@record
class Circle:
    radius: float

@record
class Square:
    side: float

type Shape = Rectangle | Circle | Square

def area(shape: Shape) -> float:
    match shape:
        case Rectangle(length=length, width=width):
            return length * width
        case Circle(radius=radius):
            return math.pi * radius**2
        case Square(side=side):
            return side * side
        case _:
            assert_never(shape)

shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0),
                       Square(5.0)]
for shape in shapes:
    print(round(area(shape), 4))
#: 3.1416
#: 12.0
#: 25.0
