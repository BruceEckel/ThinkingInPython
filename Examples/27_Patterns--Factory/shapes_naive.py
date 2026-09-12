# shapes_naive.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @abstractmethod
    def svg(self) -> str: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def svg(self) -> str: return '<circle r="1"/>'

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def svg(self) -> str:
        return '<rect width="1" height="1"/>'

class Triangle(Shape):
    @override
    def draw(self) -> None: print("Triangle.draw")
    @override
    def svg(self) -> str:
        return '<polygon points="0,0 1,0 0,1"/>'

def render(kind: str) -> None:
    if kind == "Circle":
        Circle().draw()
    elif kind == "Square":
        Square().draw()

def export_svg(kind: str) -> None:
    match kind:
        case "Circle":
            print(Circle().svg())
        case "Square":
            print(Square().svg())
        case _:
            raise ValueError(f"Unknown shape: {kind}")

render("Circle")
#: Circle.draw
render("Triangle")  # Draws nothing, reports nothing
export_svg("Square")
#: <rect width="1" height="1"/>
try:
    export_svg("Triangle")
except ValueError as e:
    print(e)
#: Unknown shape: Triangle
