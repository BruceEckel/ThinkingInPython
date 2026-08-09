# itertools_accumulate.py
from itertools import accumulate
from operator import mul

print(list(accumulate([1, 2, 3, 4])))
#: [1, 3, 6, 10]
print(list(accumulate([1, 2, 3, 4], mul)))
#: [1, 2, 6, 24]
