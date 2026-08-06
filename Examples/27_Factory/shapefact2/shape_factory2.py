# shapefact2/shape_factory2.py
# Polymorphic factory methods.
import random
from collections.abc import Iterator
from typing import ClassVar, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class ShapeFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {}

    # Build and cache each kind's factory on first request:
    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(f"{kind}.Factory()")
        return cls.factories[kind].create()

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
    random.seed(4)
    shapes = [ShapeFactory.create_shape(i) for i in shape_name_gen(4)]
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
