# exercise_1.py
from exceptions import expect

def bad_append(item, target=[]):
    target.append(item)
    return target

print(bad_append(1))
#: [1]
print(bad_append(2))
#: [1, 2]
print(bad_append(3))
#: [1, 2, 3]

def tuple_append(item, target=()):
    target.append(item)  # type: ignore
    return target

expect(AttributeError, tuple_append, 1)
#: [AttributeError] 'tuple' object has no attribute 'append'
