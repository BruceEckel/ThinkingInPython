# explicit_generator.py
import random
from shapefact1.shape_factory1 import shape_name_gen

random.seed(47)

gen = shape_name_gen(7)
print(next(gen))
#: Square
print(next(gen))
#: Circle
