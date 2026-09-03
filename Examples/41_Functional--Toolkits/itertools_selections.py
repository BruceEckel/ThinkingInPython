# itertools_selections.py
from itertools import (combinations,
                       combinations_with_replacement,
                       permutations, product)

print(list(permutations("AB", 2)))
#: [('A', 'B'), ('B', 'A')]
print(list(combinations("AB", 2)))
#: [('A', 'B')]
print(list(combinations_with_replacement("AB", 2)))
#: [('A', 'A'), ('A', 'B'), ('B', 'B')]
print(list(product("AB", repeat=2)))
#: [('A', 'A'), ('A', 'B'), ('B', 'A'), ('B', 'B')]
