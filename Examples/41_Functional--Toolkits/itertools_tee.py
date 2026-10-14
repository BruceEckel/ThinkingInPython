# itertools_tee.py
from itertools import tee

a, b = tee([1, 2, 3])
print(list(a), list(b))
#: [1, 2, 3] [1, 2, 3]
source = iter([1, 2, 3])
a, b = tee(source)
next(source)  # [1]
print(list(a), list(b))
#: [2, 3] [2, 3]
