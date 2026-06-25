# flower_visitors.py
# Demonstration of "visitor" pattern.
import random
from collections.abc import Iterator
from typing import Any

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
class Runuculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

# The companion class accepted by Flower:
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

# It's almost as if I had a method to Perform
# various "Bug" operations on all Flowers:
bee = Bee()
fly = Fly()
worm = Worm()
for flower in flower_gen(10):
    flower.accept(bee)
    flower.accept(fly)
    flower.accept(worm)
## Gladiolus pollinated by Bee
## Gladiolus pollinated by Fly
## Gladiolus eaten by Worm
## Chrysanthemum pollinated by Bee
## Chrysanthemum pollinated by Fly
## Chrysanthemum eaten by Worm
## Gladiolus pollinated by Bee
## Gladiolus pollinated by Fly
## Gladiolus eaten by Worm
## Chrysanthemum pollinated by Bee
## Chrysanthemum pollinated by Fly
## Chrysanthemum eaten by Worm
## Chrysanthemum pollinated by Bee
## Chrysanthemum pollinated by Fly
## Chrysanthemum eaten by Worm
## Chrysanthemum pollinated by Bee
## Chrysanthemum pollinated by Fly
## Chrysanthemum eaten by Worm
## Gladiolus pollinated by Bee
## Gladiolus pollinated by Fly
## Gladiolus eaten by Worm
## Runuculus pollinated by Bee
## Runuculus pollinated by Fly
## Runuculus eaten by Worm
## Gladiolus pollinated by Bee
## Gladiolus pollinated by Fly
## Gladiolus eaten by Worm
## Chrysanthemum pollinated by Bee
## Chrysanthemum pollinated by Fly
## Chrysanthemum eaten by Worm
