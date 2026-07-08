# itertools_filterfalse.py
from itertools import filterfalse

print(list(filterfalse(lambda n: n % 2 == 0, range(6))))
#: [1, 3, 5]
