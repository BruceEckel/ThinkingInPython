# shapes_match.py
# The same shapes as immutable data, with one free function that
# dispatches by pattern matching. No base class and no overridden
# methods.
import math
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Rectangle:
    length: float
    width: float

@dataclass(frozen=True)
class Circle:
    radius: float

type Shape = Rectangle | Circle

def area(shape: Shape) -> float:
    match shape:
        case Rectangle(length=length, width=width):
            return length * width
        case Circle(radius=radius):
            return math.pi * radius**2
        case _:
            assert_never(shape)

if __name__ == "__main__":
    shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0)]
    for shape in shapes:
        print(round(area(shape), 4))
#: 3.1416
#: 12.0
