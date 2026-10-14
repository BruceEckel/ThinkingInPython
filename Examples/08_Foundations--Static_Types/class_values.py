# class_values.py
from typing import reveal_type

class Shape:
    pass

class Circle(Shape):
    pass

def make(kind: type[Shape]) -> Shape:
    return kind()

shape = make(Circle)
reveal_type(shape)  # ty: Shape
print(type(shape).__name__)
#: Circle
