# shapefact1/shape_factory1.py
# A simple static factory method.
import random
from collections.abc import Iterator


class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...
    # Create based on class name:
    @staticmethod
    def factory(type: str) -> Shape:
        if type == "Circle":
            return Circle()
        if type == "Square":
            return Square()
        raise ValueError(f"Bad shape creation: {type}")

class Circle(Shape):
    def draw(self) -> None: print("Circle.draw")
    def erase(self) -> None: print("Circle.erase")

class Square(Shape):
    def draw(self) -> None: print("Square.draw")
    def erase(self) -> None: print("Square.erase")

# Generate shape name strings:
def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__

shapes = \
  [ Shape.factory(i) for i in shape_name_gen(7)]

for shape in shapes:
    shape.draw()
    shape.erase()
