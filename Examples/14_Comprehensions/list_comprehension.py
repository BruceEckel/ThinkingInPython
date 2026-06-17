# list_comprehension.py
a_list = [1, "4", 9, "a", 0, 4]
squared_ints = [e ** 2 for e in a_list if isinstance(e, int)]
print(squared_ints)
# [1, 81, 0, 16]
