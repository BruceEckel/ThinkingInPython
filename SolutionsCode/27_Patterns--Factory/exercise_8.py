# exercise_8.py
from typing import ClassVar, Final, Protocol, override

class Shape:
    def draw(self) -> None: ...

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    class Factory:
        def create(self) -> _Circle: return _Circle()

class EvalFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {}

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(f"_{kind}.Factory()")
        return cls.factories[kind].create()

# A shape "name" that is really an expression:
ATTACK: Final[str] = (
    "Circle.Factory() if print('side effect!')"
    " else _Circle")
EvalFactory.create_shape(ATTACK).draw()
#: side effect!
#: Circle.draw

class TableFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {
        "Circle": _Circle.Factory(),
    }

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        return cls.factories[kind].create()

TableFactory.create_shape("Circle").draw()
#: Circle.draw
try:
    TableFactory.create_shape(ATTACK)
except KeyError as e:
    print(type(e).__name__)
#: KeyError
