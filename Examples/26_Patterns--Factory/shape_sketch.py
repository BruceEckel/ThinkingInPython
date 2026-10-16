# shape_sketch.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

class Sketch(ABC):
    # The factory method:
    @abstractmethod
    def new_shape(self) -> Shape: ...
    def render(self, n: int) -> None:
        for _ in range(n):
            self.new_shape().draw()

class CircleSketch(Sketch):
    @override
    def new_shape(self) -> Shape: return Circle()

class SquareSketch(Sketch):
    @override
    def new_shape(self) -> Shape: return Square()

for sketch in (CircleSketch(), SquareSketch()):
    sketch.render(2)
#: Circle.draw
#: Circle.draw
#: Square.draw
#: Square.draw
