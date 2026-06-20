# set_methods.py
a = {1, 2, 3}
b = {3, 4, 5}

print(a.intersection(b))  # {3}: same as a & b
print(a.union(b))  # {1, 2, 3, 4, 5}: same as a | b
print(a.difference(b))  # {1, 2}: same as a - b
print(a.symmetric_difference(b))  # {1, 2, 4, 5}: same as a ^ b
print(a.intersection([2, 3, 9]))  # {2, 3}: arg can be any iterable
print(a.union(b, [6, 7]))  # {1, 2, 3, 4, 5, 6, 7}: several args
print(a.isdisjoint({8, 9}))  # True: no operator form
