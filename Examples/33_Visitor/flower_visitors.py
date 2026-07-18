# flower_visitors.py
import random
from collections.abc import Iterator
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
        return self.__class__.__name__

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
        return self.__class__.__name__

class Bug(Visitor):
    pass
class Pollinator(Bug):
    pass
class Predator(Bug):
    pass

# Add the ability to do "Bee" activities:
class Bee(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

# Add the ability to do "Fly" activities:
class Fly(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

# Add the ability to do "Worm" activities:
class Worm(Predator):
    def visit(self, flower: Flower) -> None:
        flower.eat(self)

def flower_gen(n: int) -> Iterator[Flower]:
    flwrs = Flower.__subclasses__()
    for i in range(n):
        yield random.choice(flwrs)()

# Now we can perform Bug operations on Flowers:
bee = Bee()
fly = Fly()
worm = Worm()
random.seed(47)  # Reproducible flower sequence
for flower in flower_gen(4):
    flower.accept(bee)
    flower.accept(fly)
    flower.accept(worm)
#: Ranunculus pollinated by Bee
#: Ranunculus pollinated by Fly
#: Ranunculus eaten by Worm
#: Gladiolus pollinated by Bee
#: Gladiolus pollinated by Fly
#: Gladiolus eaten by Worm
#: Ranunculus pollinated by Bee
#: Ranunculus pollinated by Fly
#: Ranunculus eaten by Worm
#: Chrysanthemum pollinated by Bee
#: Chrysanthemum pollinated by Fly
#: Chrysanthemum is toxic to Worm
