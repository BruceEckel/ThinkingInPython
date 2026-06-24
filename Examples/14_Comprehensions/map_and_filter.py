# map_and_filter.py
from a_list import a_list

print(list(map(lambda e: e ** 2,
               filter(lambda e: isinstance(e, int), a_list))))
# [1, 81, 0, 16]
