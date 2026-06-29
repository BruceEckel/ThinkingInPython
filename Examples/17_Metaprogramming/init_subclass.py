# init_subclass.py
# Track the "leaf" subclasses (those with no subclasses of their own),
# using __init_subclass__ instead of a metaclass.
from typing import ClassVar

class Color:
    registry: ClassVar[set[type[Color]]] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Color.registry.add(cls)
        Color.registry -= set(cls.__bases__)  # Keep only the leaves

class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['Blue', 'Green', 'Red']

class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Green', 'PhthaloBlue', 'Red']

# A second, independent hierarchy keeps its own registry:
class Shape:
    registry: ClassVar[set[type[Shape]]] = set()

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
#: ['Circle', 'Square']
