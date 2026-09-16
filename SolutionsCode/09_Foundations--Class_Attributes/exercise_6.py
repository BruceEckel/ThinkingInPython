# exercise_6.py
from exceptions import ignore

class A:
    x = 100

a = A()
a.x = 1
print(vars(a), a.x)
#: {'x': 1} 1
del a.x
print(vars(a), a.x)
#: {} 100
with ignore(AttributeError):
    del a.x
#: AttributeError("'A' object has no attribute 'x'")
