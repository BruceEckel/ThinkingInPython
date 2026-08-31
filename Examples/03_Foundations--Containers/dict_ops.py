# dict_ops.py

a = {"x": 1, "y": 2}
b = {"y": 20, "z": 3}
print(a | b)  # Merge; the right side wins a collision
#: {'x': 1, 'y': 20, 'z': 3}
print(a.pop("x"), a)  # Remove and return
#: 1 {'y': 2}
del b["z"]
print(b)
#: {'y': 20}
print(dict(zip("abc", [1, 2, 3])))  # Build from pairs
#: {'a': 1, 'b': 2, 'c': 3}
