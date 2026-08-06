# variance.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

def draw_all(shapes: Sequence[Shape]) -> int:
    return len(shapes)

def add_square(shapes: list[Shape]) -> None:
    shapes.append(Shape())

circles: list[Circle] = [Circle(), Circle()]
print(draw_all(circles))
#: 2
# ty: expected "list[Shape]", found "list[Circle]":
# add_square(circles)
