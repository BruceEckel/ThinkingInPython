# sets.py

a = {1, 2, 3, 3}  # Duplicates collapse
b = {3, 4, 5}
print(a)          # {1, 2, 3}
print(a & b)      # {3}: intersection
print(a | b)      # {1, 2, 3, 4, 5}: union
print(a - b)      # {1, 2}: difference
print(2 in a)     # True
