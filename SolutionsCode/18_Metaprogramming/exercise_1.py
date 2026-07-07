# exercise_1.py
from typing import ClassVar

class Color:
    registry: ClassVar[set[type[Color]]] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Color.registry.add(cls)
        Color.registry -= set(cls.__bases__)

class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass

class Yellow(Color):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Green', 'PhthaloBlue', 'Red', 'Yellow']

class MutedYellow(Yellow):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Green', 'MutedYellow', 'PhthaloBlue', 'Red']
