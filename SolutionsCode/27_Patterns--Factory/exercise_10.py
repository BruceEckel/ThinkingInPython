# exercise_10.py
from typing import Final, Protocol, runtime_checkable

@runtime_checkable
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

class Hexagon:
    def draw(self) -> None: print("Hexagon.draw")

def make(name: str) -> Shape:
    return REGISTRY[name]()

def unregistered(namespace: dict[str, object]) -> list[str]:
    return sorted(
        name
        for name, obj in namespace.items()
        if isinstance(obj, type)
        and obj is not Shape
        and issubclass(obj, Shape)
        and obj not in REGISTRY.values()
    )

Hexagon().draw()
#: Hexagon.draw
try:
    make("Hexagon")
except KeyError as e:
    print("KeyError:", e)
#: KeyError: 'Hexagon'
print(unregistered(globals()))
#: ['Hexagon']
