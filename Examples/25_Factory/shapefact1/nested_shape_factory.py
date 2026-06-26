# shapefact1/nested_shape_factory.py
import random
from collections.abc import Iterator
from typing import override

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...

def factory(kind: str) -> Shape:
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

    if kind == "Circle":
        return Circle()
    if kind == "Square":
        return Square()
    raise ValueError(f"Bad shape creation: {kind}")

def shape_name_gen(n: int) -> Iterator[Shape]:
    for i in range(n):
        yield factory(random.choice(["Circle", "Square"]))

if __name__ == "__main__":
    random.seed(47)  # Reproducible shape sequence
    # Circle()  # Not defined outside factory()
    for shape in shape_name_gen(7):
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
