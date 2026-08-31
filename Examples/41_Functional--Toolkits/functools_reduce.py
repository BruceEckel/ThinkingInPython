# functools_reduce.py
from functools import reduce
from operator import add

print(reduce(add, [1, 2, 3, 4]))
#: 10
