# itertools_takewhile.py
from itertools import takewhile

print(list(takewhile(lambda n: n < 3, [1, 2, 3, 4, 1])))
#: [1, 2]
