# list_comprehension.py
from a_list import a_list

squared_ints = [e ** 2 for e in a_list if isinstance(e, int)]
print(squared_ints)
# [1, 81, 0, 16]
