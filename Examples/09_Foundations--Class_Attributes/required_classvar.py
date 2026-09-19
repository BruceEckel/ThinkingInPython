# required_classvar.py
from typing import ClassVar
from exceptions import expected

class Shape:
    sides: ClassVar[int]  # Subclasses supply it

class Square(Shape):
    sides = 4

class Blob(Shape):
    pass

print(Square.sides)
#: 4
with expected(AttributeError):
    print(Blob.sides)
#: [AttributeError] type object 'Blob' has no attribute
#: 'sides'
