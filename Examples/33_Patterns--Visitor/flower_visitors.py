# flower_visitors.py
from typing import Any, override

# The Flower hierarchy cannot be changed:
class Flower:
    def accept(self, visitor: Any) -> None:
        visitor.visit(self)
    def pollinate(self, pollinator: Visitor) -> None:
        print(self, "pollinated by", pollinator)
    def eat(self, eater: Visitor) -> None:
        print(self, "eaten by", eater)
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass

class Chrysanthemum(Flower):
    @override
    def eat(self, eater: Visitor) -> None:
        print(self, "is toxic to", eater)

# The secondary hierarchy accepted by Flower:
class Visitor:
    def __str__(self) -> str:
        return type(self).__name__

class Bug(Visitor):
    pass

# The middle layer names the operation:
class Pollinator(Bug):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

class Predator(Bug):
    def visit(self, flower: Flower) -> None:
        flower.eat(self)

# Concrete visitors, grouped by the operation they perform:
class Bee(Pollinator):
    pass
class Fly(Pollinator):
    pass
class Worm(Predator):
    pass
