# factory/shapefact2/ShapeFactory2.py
# Polymorphic factory methods.
from __future__ import generators
import random

class ShapeFactory:
    factories = {}
    def addFactory(id, shapeFactory):
        ShapeFactory.factories.put[id] = shapeFactory
    addFactory = staticmethod(addFactory)
    # A Template Method:
    def createShape(id):
        if not ShapeFactory.factories.has_key(id):
            ShapeFactory.factories[id] = \
              eval(id + '.Factory()')
        return ShapeFactory.factories[id].create()
    createShape = staticmethod(createShape)

class Shape(object): pass

class Circle(Shape):
    def draw(self): print("Circle.draw")
    def erase(self): print("Circle.erase")
    class Factory:
        def create(self): return Circle()

class Square(Shape):
    def draw(self):
        print("Square.draw")
    def erase(self):
        print("Square.erase")
    class Factory:
        def create(self): return Square()

def shapeNameGen(n):
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__

shapes = [ ShapeFactory.createShape(i)
           for i in shapeNameGen(7)]

for shape in shapes:
    shape.draw()
    shape.erase()