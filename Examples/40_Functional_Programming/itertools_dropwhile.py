# itertools_dropwhile.py
from itertools import dropwhile

print(list(dropwhile(lambda n: n < 3, [1, 2, 3, 4, 1])))
#: [3, 4, 1]
