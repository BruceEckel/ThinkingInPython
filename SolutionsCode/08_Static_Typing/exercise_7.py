# exercise_7.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

def count(shapes: Sequence[Shape]) -> int:
    return len(shapes)

def add_square(shapes: Sequence[Shape]) -> None:
    # ty: object of type "Sequence[Shape]" has no attribute "append":
    # shapes.append(Shape())
    print("would add a square to", len(shapes), "shapes")

circles: list[Circle] = [Circle(), Circle()]
add_square(circles)  # Now accepted
#: would add a square to 2 shapes
print(count(circles))
#: 2
