# Metaclasses/RegisterLeafClasses.py

class RegisterLeafClasses(type):
    def __init__(cls, name, bases, nmspc):
        super(RegisterLeafClasses, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = set()
        cls.registry.add(cls)
        cls.registry -= set(bases) # Remove base classes
    # Metamethods, called on class objects:
    def __iter__(cls):
        return iter(cls.registry)
    def __str__(cls):
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])

class Color(object):
    __metaclass__ = RegisterLeafClasses

class Blue(Color): pass
class Red(Color): pass
class Green(Color): pass
class Yellow(Color): pass
print(Color)
class PhthaloBlue(Blue): pass
class CeruleanBlue(Blue): pass
print(Color)
for c in Color: # Iterate over subclasses
    print(c)

class Shape(object):
    __metaclass__ = RegisterLeafClasses

class Round(Shape): pass
class Square(Shape): pass
class Triangular(Shape): pass
class Boxy(Shape): pass
print(Shape)
class Circle(Round): pass
class Ellipse(Round): pass
print(Shape)

""" Output:
Color: Red, Blue, Green, Yellow
Color: Red, CeruleanBlue, Green, PhthaloBlue, Yellow
Red
CeruleanBlue
Green
PhthaloBlue
Yellow
Shape: Square, Round, Boxy, Triangular
Shape: Square, Ellipse, Circle, Boxy, Triangular
"""
