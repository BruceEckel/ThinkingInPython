# shape_table.py
from typing import Final, override

class Shape:
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

SHAPES: Final[dict[str, type[Shape]]] = {
    "Circle": Circle,
    "Square": Square,
}

def make(kind: str) -> Shape:
    return SHAPES[kind]()

make("Circle").draw()
#: Circle.draw
make("Square").draw()
#: Square.draw
