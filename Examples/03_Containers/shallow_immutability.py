# shallow_immutability.py

nested = (1, [2, 3])
nested[1].append(4)  # The tuple's element is still mutable
print(nested)
#: (1, [2, 3, 4])
try:
    hash(nested)  # So the tuple cannot be hashed
except TypeError as e:
    print(type(e).__name__)
#: TypeError
try:
    nested[0] = 9  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
