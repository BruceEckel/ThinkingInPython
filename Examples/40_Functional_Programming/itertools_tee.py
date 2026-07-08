# itertools_tee.py
from itertools import tee

a, b = tee([1, 2, 3])
print(list(a), list(b))
#: [1, 2, 3] [1, 2, 3]
