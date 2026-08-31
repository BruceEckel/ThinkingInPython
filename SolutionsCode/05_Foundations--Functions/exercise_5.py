# exercise_5.py
def apply_twice(func, value):
    return func(func(value))

print(apply_twice(lambda s: s + "!", "hi"))
#: hi!!
print(apply_twice(lambda n: n * n, 3))
#: 81
