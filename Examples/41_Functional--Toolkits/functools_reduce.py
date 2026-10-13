# functools_reduce.py
from functools import reduce
from operator import or_

print(reduce(or_, [{"a": 1}, {"b": 2}, {"a": 3}], {}))
#: {'a': 3, 'b': 2}
