# exercise_8.py
from typing import ClassVar, Final, Protocol, override

class Shape:
    def draw(self) -> None: ...

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    class Factory:
        def create(self) -> Circle: return Circle()

class EvalFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {}

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(f"{kind}.Factory()")
        return cls.factories[kind].create()

# A shape "name" that is really an expression:
ATTACK: Final[str] = "print('side effect!') or Circle"
EvalFactory.create_shape(ATTACK).draw()
#: side effect!
#: Circle.draw

class TableFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {
        "Circle": Circle.Factory(),
    }

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        return cls.factories[kind].create()

TableFactory.create_shape("Circle").draw()
#: Circle.draw
try:
    TableFactory.create_shape(ATTACK)
except KeyError as e:
    print(type(e).__name__, e)
#: KeyError "print('side effect!') or Circle"
