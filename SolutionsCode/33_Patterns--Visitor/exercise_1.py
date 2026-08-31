# exercise_1.py
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

@singledispatch
def pollinate(flower: Flower, agent: str) -> str:
    return f"{flower} pollinated by {agent}"

@singledispatch
def eat(flower: Flower) -> str:
    return f"{flower} eaten by Worm"

@eat.register
def _(flower: Chrysanthemum) -> str:
    return f"{flower} is toxic to Worm"

for flower in (Ranunculus(), Chrysanthemum()):
    print(pollinate(flower, "Bee"))
    print(eat(flower))
#: Ranunculus pollinated by Bee
#: Ranunculus eaten by Worm
#: Chrysanthemum pollinated by Bee
#: Chrysanthemum is toxic to Worm
