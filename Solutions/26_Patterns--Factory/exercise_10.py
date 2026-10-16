# exercise_10.py
from typing import Protocol, runtime_checkable
from exceptions import expect

@runtime_checkable
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

make = ShapeFactory()

@make.register
class Circle:
    def draw(self) -> None: print("Circle.draw")

@make.register
class Square:
    def draw(self) -> None: print("Square.draw")

class Hexagon:
    def draw(self) -> None: print("Hexagon.draw")

def unregistered(namespace: dict[str, object]) -> list[str]:
    return sorted(
        name
        for name, obj in namespace.items()
        if isinstance(obj, type)
        and obj is not Shape
        and issubclass(obj, Shape)
        and obj not in make.registry.values()
    )

Hexagon().draw()
#: Hexagon.draw
expect(KeyError, make, "Hexagon")
#: [KeyError] 'Hexagon'
print(unregistered(globals()))
#: ['Hexagon']
