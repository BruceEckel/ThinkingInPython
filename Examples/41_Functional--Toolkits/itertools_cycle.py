# itertools_cycle.py
from itertools import cycle, islice

print(list(islice(cycle("AB"), 5)))
#: ['A', 'B', 'A', 'B', 'A']
