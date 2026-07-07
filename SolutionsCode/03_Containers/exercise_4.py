# exercise_4.py
groups = {frozenset({1, 2}), frozenset({3, 4})}
try:
    groups.add([1, 2])
except TypeError as e:
    print(type(e).__name__)
    print(e)
#: TypeError
#: cannot use 'list' as a set element (unhashable type: 'list')
