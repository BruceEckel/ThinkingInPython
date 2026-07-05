# unpacking_comprehensions.py
rows = [[1, 2], [3, 4], [5]]
dicts = [{"a": 1}, {"b": 2}, {"a": 3}]

# * splices each iterable into the result:
print([*row for row in rows])
#: [1, 2, 3, 4, 5]

# ** merges each mapping; later keys win, order preserved:
print({**d for d in dicts})
#: {'a': 3, 'b': 2}

# The same syntax works in a generator expression:
flat = (*row for row in rows)
print(list(flat))
#: [1, 2, 3, 4, 5]
