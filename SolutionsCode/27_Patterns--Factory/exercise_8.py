# exercise_8.py
from abc import ABC, abstractmethod
from typing import Final, Protocol, override
from exceptions import expect

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    class Factory:
        def create(self) -> _Circle: return _Circle()

def eval_shape(kind: str) -> Shape:
    maker: ShapeMaker = eval(f"_{kind}.Factory()")
    return maker.create()

# A shape "name" that is really an expression:
ATTACK: Final[str] = (
    "Circle.Factory() if print('side effect!')"
    " else _Circle")
eval_shape(ATTACK).draw()
#: side effect!
#: Circle.draw

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": _Circle.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

create_shape("Circle").draw()
#: Circle.draw
expect(KeyError, create_shape, ATTACK)
#: [KeyError] "Circle.Factory() if print('side effect!')
#: else _Circle"
