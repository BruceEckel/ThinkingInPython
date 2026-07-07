# itertools_count.py
from itertools import count, islice

print(list(islice(count(10, 2), 5)))
#: [10, 12, 14, 16, 18]
