# shapes_oo.py
# The classic object-oriented shapes: an abstract base class with an
# overridden method, dispatched by inheritance.
import math
from abc import ABC, abstractmethod
from typing import override


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Rectangle(Shape):
    def __init__(self, length: float, width: float) -> None:
        self.length = length
        self.width = width

    @override
    def area(self) -> float:
        return self.length * self.width


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @override
    def area(self) -> float:
        return math.pi * self.radius**2


if __name__ == "__main__":
    shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0)]
    for shape in shapes:
        print(round(shape.area(), 4))
