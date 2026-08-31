# itertools_product.py
from itertools import product

print(list(product("AB", [1, 2])))
#: [('A', 1), ('A', 2), ('B', 1), ('B', 2)]
