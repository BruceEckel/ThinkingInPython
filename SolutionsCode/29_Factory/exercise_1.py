# exercise_1.py
from __future__ import annotations

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
    def draw(self) -> None:
        print("Circle.draw")

    def erase(self) -> None:
        print("Circle.erase")

class Square(Shape):
    def draw(self) -> None:
        print("Square.draw")

    def erase(self) -> None:
        print("Square.erase")

class Triangle(Shape):
    def draw(self) -> None:
        print("Triangle.draw")

    def erase(self) -> None:
        print("Triangle.erase")

s = Shape.factory("Triangle")
s.draw()
#: Triangle.draw
s.erase()
#: Triangle.erase
