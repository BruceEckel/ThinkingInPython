# itertools_dropwhile.py
from itertools import dropwhile, filterfalse

def small(n: int) -> bool:
    return n < 3

data = [1, 2, 3, 4, 1]
print(list(dropwhile(small, data)))
#: [3, 4, 1]
print(list(filterfalse(small, data)))
#: [3, 4]
