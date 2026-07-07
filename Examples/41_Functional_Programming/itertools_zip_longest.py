# itertools_zip_longest.py
from itertools import zip_longest

print(list(zip_longest([1, 2, 3], [4, 5])))
#: [(1, 4), (2, 5), (3, None)]
