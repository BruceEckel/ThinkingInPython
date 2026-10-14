# recursive_accept.py
from typing import Any, Protocol
from flower_visitors import Bee, Gladiolus, Ranunculus, Worm

class Accepts(Protocol):
    def accept(self, visitor: Any) -> None: ...

# accept() drives the traversal itself:
class Corsage:
    def __init__(self, *elements: Accepts) -> None:
        self.elements = elements

    def accept(self, visitor: Any) -> None:
        for element in self.elements:
            element.accept(visitor)

if __name__ == "__main__":
    corsage = Corsage(
        Gladiolus(), Corsage(Ranunculus()))
    for bug in (Bee(), Worm()):
        corsage.accept(bug)
#: Gladiolus pollinated by Bee
#: Ranunculus pollinated by Bee
#: Gladiolus eaten by Worm
#: Ranunculus eaten by Worm
