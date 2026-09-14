# exercise_4.py
from abc import ABC, abstractmethod
from typing import Protocol, override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    def __init__(self, thickness: str) -> None:
        self.thickness = thickness

    @override
    def draw(self) -> None:
        print(f"{self.thickness} Circle.draw")

class Square(Shape):
    def __init__(self, thickness: str) -> None:
        self.thickness = thickness

    @override
    def draw(self) -> None:
        print(f"{self.thickness} Square.draw")

class ShapeFactory(Protocol):
    def make_circle(self) -> Shape: ...
    def make_square(self) -> Shape: ...

class ThickShapeFactory:
    def make_circle(self) -> Shape:
        return Circle("thick")

    def make_square(self) -> Shape:
        return Square("thick")

class ThinShapeFactory:
    def make_circle(self) -> Shape:
        return Circle("thin")

    def make_square(self) -> Shape:
        return Square("thin")

def build_shapes(factory: ShapeFactory) -> list[Shape]:
    return [factory.make_circle(), factory.make_square()]

for shape in build_shapes(ThickShapeFactory()):
    shape.draw()
#: thick Circle.draw
#: thick Square.draw
for shape in build_shapes(ThinShapeFactory()):
    shape.draw()
#: thin Circle.draw
#: thin Square.draw
