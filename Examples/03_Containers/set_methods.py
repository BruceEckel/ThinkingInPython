# set_methods.py
a = {1, 2, 3}
b = {3, 4, 5}

print(a.intersection(b))  # Same as a & b
#: {3}
print(a.union(b))  # Same as a | b
#: {1, 2, 3, 4, 5}
print(a.difference(b))  # Same as a - b
#: {1, 2}
print(a.symmetric_difference(b))  # Same as a ^ b
#: {1, 2, 4, 5}
print(a.intersection([2, 3, 9]))  # Arg can be any iterable
#: {2, 3}
print(a.union(b, [6, 7]))  # Several args
#: {1, 2, 3, 4, 5, 6, 7}
print(a.isdisjoint({8, 9}))  # No operator form
#: True
