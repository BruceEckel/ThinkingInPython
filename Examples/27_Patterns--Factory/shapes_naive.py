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

def render(kind: str) -> None:
    match kind:
        case "Circle":
            Circle().draw()
        case "Square":
            Square().draw()

def export_svg(kind: str) -> None:
    match kind:
        case "Circle":
            Circle().draw()
        case "Square":
            Square().draw()

render("Circle")
#: Circle.draw
export_svg("Square")
#: Square.draw
