# filter_then_map.py
from a_list import a_list

ints = list(filter(lambda e: isinstance(e, int), a_list))
print(ints)
#: [1, 9, 0, 4]
print(list(map(lambda e: e ** 2, ints)))  # type: ignore
#: [1, 81, 0, 16]
