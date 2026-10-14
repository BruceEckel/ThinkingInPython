# shape_factory_objects.py
from abc import ABC, abstractmethod
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    class Factory:
        def create(self) -> _Circle: return _Circle()

class _Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    class Factory:
        def create(self) -> _Square: return _Square()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": _Circle.Factory(),
    "Square": _Square.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

for kind in ["Circle", "Square", "Circle"]:
    create_shape(kind).draw()
#: Circle.draw
#: Square.draw
#: Circle.draw
