# variance.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

class Square(Shape):
    pass

def count(shapes: Sequence[Shape]) -> int:
    return len(shapes)

def add_square(shapes: list[Shape]) -> None:
    shapes.append(Square())

circles: list[Circle] = [Circle(), Circle()]
print(count(circles))
#: 2
# ty: expected "list[Shape]", found "list[Circle]":
# add_square(circles)
