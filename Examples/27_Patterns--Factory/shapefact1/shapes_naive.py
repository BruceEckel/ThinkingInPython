# shapefact1/shapes_naive.py
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
    if kind == "Circle":
        Circle().draw()
    elif kind == "Square":
        Square().draw()

def preview(kind: str) -> None:
    if kind == "Circle":
        Circle().draw()
    elif kind == "Square":
        Square().draw()

def export_svg(kind: str) -> None:
    if kind == "Circle":
        Circle().draw()
    elif kind == "Square":
        Square().draw()

render("Circle")
#: Circle.draw
preview("Square")
#: Square.draw
export_svg("Circle")
#: Circle.draw
