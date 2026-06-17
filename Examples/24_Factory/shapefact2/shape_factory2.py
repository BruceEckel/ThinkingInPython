# shapefact2/shape_factory2.py
# Polymorphic factory methods.
import random
from collections.abc import Iterator
from typing import Any


class ShapeFactory:
    factories: dict[str, Any] = {}

    @staticmethod
    def add_factory(id: str, shape_factory: Any) -> None:
        ShapeFactory.factories[id] = shape_factory

    # A Template Method:
    @staticmethod
    def create_shape(id: str) -> Shape:
        if id not in ShapeFactory.factories:
            ShapeFactory.factories[id] = eval(id + '.Factory()')
        return ShapeFactory.factories[id].create()


class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...


class Circle(Shape):
    def draw(self) -> None: print("Circle.draw")
    def erase(self) -> None: print("Circle.erase")
    class Factory:
        def create(self) -> Circle: return Circle()


class Square(Shape):
    def draw(self) -> None:
        print("Square.draw")
    def erase(self) -> None:
        print("Square.erase")
    class Factory:
        def create(self) -> Square: return Square()


def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__


shapes = [ShapeFactory.create_shape(i) for i in shape_name_gen(7)]

for shape in shapes:
    shape.draw()
    shape.erase()
