# itertools_chain.py
from itertools import chain

print(list(chain([1, 2], [3, 4])))
#: [1, 2, 3, 4]
print(list(chain.from_iterable([[1, 2], [3, 4]])))
#: [1, 2, 3, 4]
