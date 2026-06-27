# sets.py

a = {1, 2, 3, 3}  # Duplicates collapse
b = {3, 4, 5}
print(a)
#: {1, 2, 3}
print(a & b)      # Intersection
#: {3}
print(a | b)      # Union
#: {1, 2, 3, 4, 5}
print(a - b)      # Difference
#: {1, 2}
print(2 in a)
#: True
