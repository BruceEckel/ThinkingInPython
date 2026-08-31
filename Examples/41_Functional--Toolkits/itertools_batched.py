# itertools_batched.py
from itertools import batched

print(list(batched(range(7), 3)))
#: [(0, 1, 2), (3, 4, 5), (6,)]
