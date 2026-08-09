# dispatch_trace.py
from flower_visitors import Chrysanthemum, Gladiolus, Worm

worm = Worm()
for flower in (Chrysanthemum(), Gladiolus()):
    print(type(worm).visit.__qualname__,
          "then", type(flower).eat.__qualname__)
    flower.accept(worm)
#: Predator.visit then Chrysanthemum.eat
#: Chrysanthemum is toxic to Worm
#: Predator.visit then Flower.eat
#: Gladiolus eaten by Worm
