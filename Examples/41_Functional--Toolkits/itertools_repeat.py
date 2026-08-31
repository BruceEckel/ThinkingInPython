# itertools_repeat.py
from itertools import repeat

print(list(repeat("x", 3)))
#: ['x', 'x', 'x']
print(list(map(pow, range(5), repeat(2))))
#: [0, 1, 4, 9, 16]
