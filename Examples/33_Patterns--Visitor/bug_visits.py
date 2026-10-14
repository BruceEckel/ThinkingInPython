# bug_visits.py
from flower_visitors import (Bee, Chrysanthemum, Fly,
                             Gladiolus, Ranunculus, Worm)

bee = Bee()
fly = Fly()
worm = Worm()
for flower in (Gladiolus(), Ranunculus(), Chrysanthemum()):
    flower.accept(bee)
    flower.accept(fly)
    flower.accept(worm)
#: Gladiolus pollinated by Bee
#: Gladiolus pollinated by Fly
#: Gladiolus eaten by Worm
#: Ranunculus pollinated by Bee
#: Ranunculus pollinated by Fly
#: Ranunculus eaten by Worm
#: Chrysanthemum pollinated by Bee
#: Chrysanthemum pollinated by Fly
#: Chrysanthemum is toxic to Worm
