# exercise_3.py
from functools import singledispatchmethod
from typing import ClassVar

class Trash:
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init__(self, weight: float) -> None:
        self.weight = weight

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

class Aluminum(Trash):
    value = 1.67

class Paper(Trash):
    value = 0.10

class Glass(Trash):
    value = 0.23

class Cardboard(Trash):
    value = 0.79

class Plastic(Trash):
    value = 0.15

class Sorter:
    @singledispatchmethod
    def recycling_note(self, t: Trash) -> str:
        return f"{type(t).__name__}: no special handling"

    @recycling_note.register
    def _(self, t: Aluminum) -> str:
        return "Aluminum: crush and bale"

    @recycling_note.register
    def _(self, t: Glass) -> str:
        return "Glass: sort by color, then crush"

    @recycling_note.register
    def _(self, t: Cardboard) -> str:
        return "Cardboard: flatten and bundle"

sorter = Sorter()
for t in [Aluminum(1), Paper(1), Glass(1), Cardboard(1), Plastic(1)]:
    print(sorter.recycling_note(t))
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
#: Plastic: no special handling
