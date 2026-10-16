# exercise_1.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return _Circle()
            case "Square":
                return _Square()
            case "Triangle":
                return _Triangle()
            case _:
                raise ValueError(f"Bad shape: {kind}")

class _Circle(Shape):
    @override
    def draw(self) -> None:
        print("Circle.draw")

class _Square(Shape):
    @override
    def draw(self) -> None:
        print("Square.draw")

class _Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

s = Shape.factory("Triangle")
s.draw()
#: Triangle.draw
