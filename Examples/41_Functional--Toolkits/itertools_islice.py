# itertools_islice.py
from itertools import islice

it = iter(range(10))
print(list(islice(it, 2, 8, 2)))
#: [2, 4, 6]
print(next(it))
#: 8
