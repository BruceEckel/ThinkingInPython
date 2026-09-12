# shape_factory2.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @abstractmethod
    def erase(self) -> None: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")
    class Factory:
        def create(self) -> _Circle: return _Circle()

class _Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")
    class Factory:
        def create(self) -> _Square: return _Square()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": _Circle.Factory(),
    "Square": _Square.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

def shape_name(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for _ in range(n):
        cls = random.choice(types)
        yield cls.__name__.removeprefix("_")

if __name__ == "__main__":
    random.seed(4)
    shapes = [create_shape(kind) for kind in shape_name(4)]
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
