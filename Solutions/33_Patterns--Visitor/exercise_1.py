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

def pollinate(flower: Flower, pollinator: str) -> str:
    return f"{flower} pollinated by {pollinator}"

@singledispatch
def eat(flower: Flower, eater: str) -> str:
    return f"{flower} eaten by {eater}"

@eat.register
def _(flower: Chrysanthemum, eater: str) -> str:
    return f"{flower} is toxic to {eater}"

for flower in (Ranunculus(), Chrysanthemum()):
    print(pollinate(flower, "Bee"))
    print(eat(flower, "Worm"))
#: Ranunculus pollinated by Bee
#: Ranunculus eaten by Worm
#: Chrysanthemum pollinated by Bee
#: Chrysanthemum is toxic to Worm
