# Metaclasses/RegisterLeafClasses.py

class ClassSet(set):
    "Simplify printing a set of classes"
    def __str__(self):
        return "(" + ", ".join([c.__name__ for c in self]) + ")"

class RegisterLeafClasses(type):
    def __init__(cls, name, bases, nmspc):
        super(RegisterLeafClasses, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = ClassSet()
        cls.registry.add(cls)
        cls.registry -= set(bases) # Remove base classes

class Color(object):
    __metaclass__ = RegisterLeafClasses

class Blue(Color): pass
class Red(Color): pass
class Green(Color): pass
class Yellow(Color): pass
print(Color.registry)
class PhthaloBlue(Blue): pass
class CeruleanBlue(Blue): pass
print(Color.registry)

class Shape(object):
    __metaclass__ = RegisterLeafClasses

class Round(Shape): pass
class Square(Shape): pass
class Triangular(Shape): pass
class Boxy(Shape): pass
print(Shape.registry)
class Circle(Round): pass
class Ellipse(Round): pass
print(Shape.registry)

""" Output:
(Red, Blue, Yellow, Green)
(Red, CeruleanBlue, Yellow, PhthaloBlue, Green)
(Square, Round, Boxy, Triangular)
(Square, Ellipse, Boxy, Circle, Triangular)
"""