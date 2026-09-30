# shape_registry.py
from typing import Protocol

class Shape(Protocol):
    def draw(self) -> None: ...

class ShapeFactory:
    def __init__(self) -> None:
        self.registry: dict[str, type[Shape]] = {}

    def register[S: Shape](self, cls: type[S]) -> type[S]:
        self.registry[cls.__name__] = cls
        return cls

    def __call__(self, name: str) -> Shape:
        return self.registry[name]()
