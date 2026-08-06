# shape_registry.py
from typing import ClassVar

class Shape:
    registry: ClassVar[dict[str, type[Shape]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Shape.registry[cls.__name__] = cls

    def draw(self) -> None: ...

def make(kind: str) -> Shape:
    return Shape.registry[kind]()
