# shapefact1/nested_shape_factory.py
import random


class Shape:
    types = []

def factory(type):
    class Circle(Shape):
        def draw(self): print("Circle.draw")
        def erase(self): print("Circle.erase")

    class Square(Shape):
        def draw(self): print("Square.draw")
        def erase(self): print("Square.erase")

    if type == "Circle":
        return Circle()
    if type == "Square":
        return Square()
    assert 0, "Bad shape creation: " + type

def shape_name_gen(n):
    for i in range(n):
        yield factory(random.choice(["Circle", "Square"]))

# Circle() # Not defined

for shape in shape_name_gen(7):
    shape.draw()
    shape.erase()
