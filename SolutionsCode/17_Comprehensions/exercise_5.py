# exercise_5.py
dicts = [{"a": 1}, {"b": 2}, {"a": 3}, {"a": 5, "c": 9}]
print({**d for d in dicts})
#: {'a': 5, 'b': 2, 'c': 9}
