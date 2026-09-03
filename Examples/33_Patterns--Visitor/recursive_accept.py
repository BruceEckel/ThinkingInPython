# recursive_accept.py
from typing import Any
from flower_visitors import Bee, Gladiolus, Ranunculus

# accept() drives the traversal itself:
class Corsage:
    def __init__(self, *elements: Any) -> None:
        self.elements = elements

    def accept(self, visitor: Any) -> None:
        for element in self.elements:
            element.accept(visitor)

if __name__ == "__main__":
    corsage = Corsage(
        Gladiolus(), Corsage(Ranunculus()))
    corsage.accept(Bee())
#: Gladiolus pollinated by Bee
#: Ranunculus pollinated by Bee
