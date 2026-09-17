# shapes_oo.py
import math
from abc import ABC, abstractmethod
from typing import override
from record import record

class Shape(ABC):
    __slots__ = ()

    @abstractmethod
    def area(self) -> float: ...

@record
class Rectangle(Shape):
    length: float
    width: float

    @override
    def area(self) -> float:
        return self.length * self.width

@record
class Circle(Shape):
    radius: float

    @override
    def area(self) -> float:
        return math.pi * self.radius**2

if __name__ == "__main__":
    for shape in [Circle(1.0), Rectangle(3.0, 4.0)]:
        print(round(shape.area(), 4))
#: 3.1416
#: 12.0
