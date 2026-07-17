# sets.py

a = {1, 2, 3, 3}  # Duplicates collapse
print(a)
#: {1, 2, 3}
b = {3, 4, 5}
print(a & b)  # Intersection
#: {3}
print(a | b)  # Union
#: {1, 2, 3, 4, 5}
print(a - b)  # Difference
#: {1, 2}
print(a ^ b)  # Symmetric difference
#: {1, 2, 4, 5}
c = {1, 2}
print(c <= a)  # Subset
#: True
print(a >= c)  # Superset
#: True
print(2 in a)
#: True
