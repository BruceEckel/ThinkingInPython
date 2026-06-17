# shapefact1/nested_shape_factory.py
import random
from collections.abc import Iterator


class Shape:
    types: list[type] = []
    def draw(self) -> None: ...
    def erase(self) -> None: ...

def factory(type: str) -> Shape:
    class Circle(Shape):
        def draw(self) -> None: print("Circle.draw")
        def erase(self) -> None: print("Circle.erase")

    class Square(Shape):
        def draw(self) -> None: print("Square.draw")
        def erase(self) -> None: print("Square.erase")

    if type == "Circle":
        return Circle()
    if type == "Square":
        return Square()
    raise ValueError(f"Bad shape creation: {type}")

def shape_name_gen(n: int) -> Iterator[Shape]:
    for i in range(n):
        yield factory(random.choice(["Circle", "Square"]))

# Circle() # Not defined

for shape in shape_name_gen(7):
    shape.draw()
    shape.erase()
