# exercise_2.py
from abc import ABC, abstractmethod
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

    @abstractmethod
    def erase(self) -> None: ...

class _Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

    @override
    def erase(self) -> None:
        print("Triangle.erase")

    class Factory:
        def create(self) -> _Triangle:
            return _Triangle()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Triangle": _Triangle.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

create_shape("Triangle").draw()
#: Triangle.draw
