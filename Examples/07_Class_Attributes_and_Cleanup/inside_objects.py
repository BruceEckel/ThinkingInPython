# inside_objects.py

class A:
    x = 100  # class attribute


a = A()
print(vars(A)["x"])  # 100: The attribute lives in the class dict
print(vars(a))  # {}: The instance has no attributes yet
a.x = 1
print(vars(a))  # {'x': 1}: Assignment created it on the instance
print(vars(A)["x"])  # Still 100
