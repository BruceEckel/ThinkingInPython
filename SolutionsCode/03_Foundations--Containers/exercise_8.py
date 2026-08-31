# exercise_8.py

pairs = [("a", 1), ("b", 2), ("c", 3)]
counts = dict(pairs)
print(counts)
#: {'a': 1, 'b': 2, 'c': 3}
print(list(counts.keys()), list(counts.values()))
#: ['a', 'b', 'c'] [1, 2, 3]
print(counts | {"c": 30, "d": 4})
#: {'a': 1, 'b': 2, 'c': 30, 'd': 4}
print(counts)  # The merge built a new dict
#: {'a': 1, 'b': 2, 'c': 3}
