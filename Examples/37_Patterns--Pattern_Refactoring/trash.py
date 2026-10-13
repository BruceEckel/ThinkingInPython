# trash.py
from typing import ClassVar
from record import record

type Bins = dict[type[Trash], list[Trash]]

@record
class Trash:
    weight: float
    # Dollars per pound (per subclass)
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        return cls.registry[name](weight)

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Paper(Trash):
    value: ClassVar[float] = 0.10

class Glass(Trash):
    value: ClassVar[float] = 0.23

class Cardboard(Trash):
    value: ClassVar[float] = 0.79

def sum_value(contents: list[Trash]) -> float:
    return sum(piece.weight * piece.value
               for piece in contents)

def report(bins: Bins) -> None:
    for material, contents in bins.items():
        total = sum_value(contents)
        print(f"{material.__name__}: {total:.2f}")
