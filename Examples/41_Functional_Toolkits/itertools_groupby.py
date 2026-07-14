# itertools_groupby.py
from itertools import groupby

data = ["a", "a", "b", "b", "b", "c"]
print([(k, list(g)) for k, g in groupby(data)])
#: [('a', ['a', 'a']), ('b', ['b', 'b', 'b']), ('c', ['c'])]
