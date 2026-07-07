# exercise_1.py
def bad_append(item, target=[]):
    target.append(item)
    return target

print(bad_append(1))
#: [1]
print(bad_append(2))
#: [1, 2]
print(bad_append(3))
#: [1, 2, 3]
