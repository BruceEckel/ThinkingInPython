# shapes_naive.py
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

class Triangle(Shape):
    @override
    def draw(self) -> None: print("Triangle.draw")

def render(kind: str) -> None:
    if kind == "Circle":
        Circle().draw()
    elif kind == "Square":
        Square().draw()

def export_svg(kind: str) -> None:
    match kind:
        case "Circle":
            Circle().draw()
        case "Square":
            Square().draw()
        case _:
            raise ValueError(f"Unknown shape: {kind}")

render("Circle")
#: Circle.draw
render("Triangle")  # Draws nothing, reports nothing
export_svg("Square")
#: Square.draw
try:
    export_svg("Triangle")
except ValueError as e:
    print(e)
#: Unknown shape: Triangle
