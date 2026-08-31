# itertools_compress.py
from itertools import compress

print(list(compress("ABCD", [1, 0, 1, 0])))
#: ['A', 'C']
