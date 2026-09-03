# shape_table.py
from abc import ABC, abstractmethod
from typing import Final, Literal, override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

Kind = Literal["Circle", "Square"]

SHAPES: Final[dict[Kind, type[Shape]]] = {
    "Circle": Circle,
    "Square": Square,
}

def make(kind: Kind) -> Shape:
    return SHAPES[kind]()

make("Circle").draw()
#: Circle.draw
make("Square").draw()
#: Square.draw
# ty: expected Literal["Circle", "Square"],
# found Literal["Hexagon"]:
# make("Hexagon").draw()
