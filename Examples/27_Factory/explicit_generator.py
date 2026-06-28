# explicit_generator.py
# A generator-factory can be driven by hand: next() pulls the next
# object from it. shape_name_gen is reused from shape_factory1.
import random
from shapefact1.shape_factory1 import shape_name_gen

random.seed(47)  # Make the random choices reproducible

gen = shape_name_gen(7)
print(next(gen))
#: Square
print(next(gen))
#: Circle
