# exercise_6.py
class A:
    x = 100

a = A()
a.x = 1
print(vars(a), a.x)
#: {'x': 1} 1
del a.x
print(vars(a), a.x)
#: {} 100
try:
    del a.x
except AttributeError as e:
    print(type(e).__name__, e)
#: AttributeError 'A' object has no attribute 'x'
