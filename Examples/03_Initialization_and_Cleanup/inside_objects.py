# inside_objects.py
# An instance and its class each have their own attribute dictionary.
# Reading falls back to the class; assigning writes to the instance.
class A:
    x = 100  # class attribute


a = A()
print(vars(A)["x"])  # 100: the attribute lives in the class dict
print(vars(a))  # {}: the instance has no attributes yet
a.x = 1
print(vars(a))  # {'x': 1}: assignment created it on the instance
