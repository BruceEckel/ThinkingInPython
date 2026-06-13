# Factory/shapefact2/ShapeFactory2.py
# Polymorphic factory methods.
import random
from typing import Any


class ShapeFactory:
    factories: dict[str, Any] = {}

    @staticmethod
    def addFactory(id: str, shapeFactory: Any) -> None:
        ShapeFactory.factories[id] = shapeFactory

    # A Template Method:
    @staticmethod
    def createShape(id: str) -> "Shape":
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
        def create(self) -> "Circle": return Circle()


class Square(Shape):
    def draw(self) -> None:
        print("Square.draw")
    def erase(self) -> None:
        print("Square.erase")
    class Factory:
        def create(self) -> "Square": return Square()


def shapeNameGen(n: int):
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__


shapes = [ShapeFactory.createShape(i) for i in shapeNameGen(7)]

for shape in shapes:
    shape.draw()
    shape.erase()
