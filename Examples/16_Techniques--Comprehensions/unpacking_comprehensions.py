# unpacking_comprehensions.py
rows = [[1, 2], [3, 4], [5]]
dicts = [{"a": 1}, {"b": 2}, {"a": 3}]

print([*row for row in rows])
#: [1, 2, 3, 4, 5]

print({**d for d in dicts})
#: {'a': 3, 'b': 2}

print([*row for row in [[1, [2, 3]], [4]]])
#: [1, [2, 3], 4]
print({*s for s in [{1, 2}, {3}]})
#: {1, 2, 3}
