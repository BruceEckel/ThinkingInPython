# shapefact2/shape_factory2.py
# Polymorphic factory methods.
import random
from collections.abc import Iterator
from typing import Any, ClassVar, override

class ShapeFactory:
    factories: ClassVar[dict[str, Any]] = {}

    @staticmethod
    def add_factory(kind: str, shape_factory: Any) -> None:
        ShapeFactory.factories[kind] = shape_factory

    # A Template Method:
    @staticmethod
    def create_shape(kind: str) -> Shape:
        if kind not in ShapeFactory.factories:
            ShapeFactory.factories[kind] = eval(kind + '.Factory()')
        return ShapeFactory.factories[kind].create()

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
    def draw(self) -> None:
        print("Square.draw")
    @override
    def erase(self) -> None:
        print("Square.erase")
    class Factory:
        def create(self) -> Square: return Square()

def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__

if __name__ == "__main__":
    random.seed(47)  # Reproducible shape sequence
    shapes = [ShapeFactory.create_shape(i) for i in shape_name_gen(7)]
    for shape in shapes:
        shape.draw()
        shape.erase()
## Square.draw
## Square.erase
## Circle.draw
## Circle.erase
## Square.draw
## Square.erase
## Square.draw
## Square.erase
## Square.draw
## Square.erase
## Square.draw
## Square.erase
## Square.draw
## Square.erase
