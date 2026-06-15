# init_subclass.py
# Track the "leaf" subclasses (those with no subclasses of their own),
# using __init_subclass__ instead of a metaclass.


class Color:
    registry: set[type] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Color.registry.add(cls)
        Color.registry -= set(cls.__bases__)  # keep only the leaves


class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
print(sorted(c.__name__ for c in Color.registry))


class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass
print(sorted(c.__name__ for c in Color.registry))


# A second, independent hierarchy keeps its own registry:
class Shape:
    registry: set[type] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Shape.registry.add(cls)
        Shape.registry -= set(cls.__bases__)


class Round(Shape):
    pass
class Square(Shape):
    pass
class Circle(Round):
    pass
print(sorted(c.__name__ for c in Shape.registry))

""" Output:
['Blue', 'Green', 'Red']
['CeruleanBlue', 'Green', 'PhthaloBlue', 'Red']
['Circle', 'Square']
"""
