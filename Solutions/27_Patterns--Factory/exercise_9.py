# exercise_9.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @abstractmethod
    def erase(self) -> None: ...
    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return _Circle()
            case "Square":
                return _Square()
            case "Oval":
                return _Oval()
            case _:
                raise ValueError(f"Bad shape: {kind}")

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")

class _Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")

class _Oval(_Circle):
    @override
    def draw(self) -> None: print("Oval.draw")

def all_subclasses[T](cls: type[T]) -> Iterator[type[T]]:
    for sub in cls.__subclasses__():
        yield sub
        yield from all_subclasses(sub)

def names(classes: Iterable[type[Shape]]) -> list[str]:
    return [c.__name__.removeprefix("_") for c in classes]

print(names(Shape.__subclasses__()))
#: ['Circle', 'Square']
print(names(all_subclasses(Shape)))
#: ['Circle', 'Oval', 'Square']

def shape_name(n: int) -> Iterator[str]:
    for _ in range(n):
        cls = random.choice(list(all_subclasses(Shape)))
        yield cls.__name__.removeprefix("_")

random.seed(4)
for shape in [Shape.factory(s) for s in shape_name(6)]:
    shape.draw()
#: Circle.draw
#: Oval.draw
#: Circle.draw
#: Square.draw
#: Oval.draw
#: Oval.draw
