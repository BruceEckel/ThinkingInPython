# shapefact1/shape_factory1.py
# A simple static factory method.
import random


class Shape:
    # Create based on class name:
    @staticmethod
    def factory(type):
        if type == "Circle":
            return Circle()
        if type == "Square":
            return Square()
        assert 0, "Bad shape creation: " + type

class Circle(Shape):
    def draw(self): print("Circle.draw")
    def erase(self): print("Circle.erase")

class Square(Shape):
    def draw(self): print("Square.draw")
    def erase(self): print("Square.erase")

# Generate shape name strings:
def shape_name_gen(n):
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__

shapes = \
  [ Shape.factory(i) for i in shape_name_gen(7)]

for shape in shapes:
    shape.draw()
    shape.erase()
