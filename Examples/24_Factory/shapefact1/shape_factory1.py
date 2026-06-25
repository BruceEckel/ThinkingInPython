# shapefact1/shape_factory1.py
# A simple static factory method.
import random
from collections.abc import Iterator
from typing import override

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...
    # Create based on class name:
    @staticmethod
    def factory(kind: str) -> Shape:
        if kind == "Circle":
            return Circle()
        if kind == "Square":
            return Square()
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

# Generate shape name strings:
def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__

if __name__ == "__main__":
    random.seed(47)  # Reproducible shape sequence
    shapes = [Shape.factory(i) for i in shape_name_gen(7)]
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
