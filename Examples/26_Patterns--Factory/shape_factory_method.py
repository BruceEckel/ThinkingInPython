# shape_factory_method.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    # Create based on class name:
    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return _Circle()
            case "Square":
                return _Square()
            case _:
                raise ValueError(f"Bad shape: {kind}")

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class _Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

def shape_name(n: int) -> Iterator[str]:
    for _ in range(n):
        cls = random.choice(Shape.__subclasses__())
        yield cls.__name__.removeprefix("_")

if __name__ == "__main__":
    random.seed(4)  # Reproducible shape sequence
    shapes = [Shape.factory(s) for s in shape_name(4)]
    for shape in shapes:
        shape.draw()
#: Circle.draw
#: Square.draw
#: Circle.draw
#: Square.draw
