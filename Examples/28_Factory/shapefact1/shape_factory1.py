# shapefact1/shape_factory1.py
import random
from collections.abc import Iterator
from typing import override

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...
    # Create based on class name:
    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return Circle()
            case "Square":
                return Square()
            case _:
                raise ValueError(f"Bad shape creation: {kind}")

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")

def shape_name_gen(n: int) -> Iterator[str]:
    for i in range(n):
        yield random.choice(Shape.__subclasses__()).__name__

if __name__ == "__main__":
    random.seed(4)  # Reproducible shape sequence
    shapes = [Shape.factory(i) for i in shape_name_gen(4)]
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
