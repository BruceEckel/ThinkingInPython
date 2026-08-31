# shapes_oo.py
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

@dataclass(frozen=True)
class Rectangle(Shape):
    length: float
    width: float

    @override
    def area(self) -> float:
        return self.length * self.width

@dataclass(frozen=True)
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
