# exercise_1.py
from typing import override

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...

    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return Circle()
            case "Square":
                return Square()
            case "Triangle":
                return Triangle()
            case _:
                raise ValueError(f"Bad shape creation: {kind}")

class Circle(Shape):
    @override
    def draw(self) -> None:
        print("Circle.draw")

    @override
    def erase(self) -> None:
        print("Circle.erase")

class Square(Shape):
    @override
    def draw(self) -> None:
        print("Square.draw")

    @override
    def erase(self) -> None:
        print("Square.erase")

class Triangle(Shape):
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
