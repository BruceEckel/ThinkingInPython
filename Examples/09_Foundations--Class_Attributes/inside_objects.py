# inside_objects.py

class A:
    x = 100

a = A()
print(vars(a), a.x)  # Empty, so a.x comes from the class
#: {} 100
a.x = 1
print(vars(a), a.x)  # Assignment created it on the instance
#: {'x': 1} 1
print(vars(A)["x"])  # The class entry is unchanged
#: 100
