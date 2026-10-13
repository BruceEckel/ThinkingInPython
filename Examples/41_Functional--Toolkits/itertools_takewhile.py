# itertools_takewhile.py
from itertools import takewhile

def small(n: int) -> bool:
    return n < 3

data = [1, 2, 3, 4, 1]
print(list(takewhile(small, data)))
#: [1, 2]
print(list(filter(small, data)))
#: [1, 2, 1]
