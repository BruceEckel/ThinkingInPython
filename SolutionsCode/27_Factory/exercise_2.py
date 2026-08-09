# exercise_2.py
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape:
    def draw(self) -> None: ...

class Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

    class Factory:
        def create(self) -> Triangle:
            return Triangle()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Triangle": Triangle.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

create_shape("Triangle").draw()
#: Triangle.draw
