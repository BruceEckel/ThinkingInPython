# bug_visits.py
import random
from flower_visitors import Bee, Fly, Worm, flower_gen

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
