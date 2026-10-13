# itertools_groupby.py
from itertools import groupby

data = ["a", "a", "b", "b", "b", "c"]
print([(k, list(g)) for k, g in groupby(data)])
#: [('a', ['a', 'a']), ('b', ['b', 'b', 'b']), ('c', ['c'])]
# [1]
print([(k, list(g)) for k, g in groupby(["b", "a", "b"])])
#: [('b', ['b']), ('a', ['a']), ('b', ['b'])]
# [2]
print([(k, list(g))
       for k, g in groupby(sorted(["b", "a", "b"]))])
#: [('a', ['a']), ('b', ['b', 'b'])]
