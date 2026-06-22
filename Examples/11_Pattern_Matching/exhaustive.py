# exhaustive.py
# A closed union plus assert_never makes match exhaustive: forgetting
# a case becomes a type error, not a silent fall-through.
from dataclasses import dataclass
from math import pi
from typing import assert_never

@dataclass(frozen=True)
class Circle:
    radius: float

@dataclass(frozen=True)
class Square:
    side: float

type Shape = Circle | Square

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius):
            return pi * radius ** 2
        case Square(side):
            return side ** 2
        case _:
            assert_never(shape)

print(round(area(Circle(1.0)), 4))
print(area(Square(2.0)))
