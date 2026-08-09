# shapefact2/shape_factory2.py
# Polymorphic factory methods.
import random
from collections.abc import Iterator
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")
    class Factory:
        def create(self) -> Circle: return Circle()

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")
    class Factory:
        def create(self) -> Square: return Square()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": Circle.Factory(),
    "Square": Square.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for _ in range(n):
        yield random.choice(types).__name__

if __name__ == "__main__":
    random.seed(4)
    shapes = [create_shape(kind) for kind in shape_name_gen(4)]
    for shape in shapes:
        shape.draw()
        shape.erase()
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
