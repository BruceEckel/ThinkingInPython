# exercise_2.py
from __future__ import annotations
from typing import Any, ClassVar

class ShapeFactory:
    factories: ClassVar[dict[str, Any]] = {}

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(kind + ".Factory()")
        return cls.factories[kind].create()

class Shape:
    def draw(self) -> None: ...

class Triangle(Shape):
    def draw(self) -> None:
        print("Triangle.draw")

    class Factory:
        def create(self) -> Triangle:
            return Triangle()

ShapeFactory.create_shape("Triangle").draw()
#: Triangle.draw
