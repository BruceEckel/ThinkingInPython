# exercise_1.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

    @abstractmethod
    def erase(self) -> None: ...

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
                raise ValueError(
                    f"Bad shape creation: {kind}")

class _Circle(Shape):
    @override
    def draw(self) -> None:
        print("Circle.draw")

    @override
    def erase(self) -> None:
        print("Circle.erase")

class _Square(Shape):
    @override
    def draw(self) -> None:
        print("Square.draw")

    @override
    def erase(self) -> None:
        print("Square.erase")

class _Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

    @override
    def erase(self) -> None:
        print("Triangle.erase")

s = Shape.factory("Triangle")
s.draw()
#: Triangle.draw
s.erase()
#: Triangle.erase
