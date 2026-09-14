# protocol_registry.py
from typing import Final, Protocol

class Shape(Protocol):
    def draw(self) -> None: ...

REGISTRY: Final[dict[str, type[Shape]]] = {}

def register[S: Shape](cls: type[S]) -> type[S]:
    REGISTRY[cls.__name__] = cls
    return cls

@register
class Circle:
    def draw(self) -> None: print("Circle.draw")

@register
class Square:
    def draw(self) -> None: print("Square.draw")

def make(name: str) -> Shape:
    return REGISTRY[name]()

print(sorted(REGISTRY))
#: ['Circle', 'Square']
make("Circle").draw()
#: Circle.draw
# ty: Argument type `Blob` does not satisfy
# upper bound `Shape` of type variable `S`:
# @register
# class Blob:
#     pass
