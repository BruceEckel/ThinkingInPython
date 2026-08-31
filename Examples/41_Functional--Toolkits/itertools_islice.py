# itertools_islice.py
from itertools import islice

print(list(islice(range(10), 2, 8, 2)))
#: [2, 4, 6]
