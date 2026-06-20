# references.py

x = 10        # x names an int
x = "ten"     # The same name now binds to a str
a = [1, 2, 3]
b = a         # b binds to the same list, not a copy
b.append(4)
print(a)       # [1, 2, 3, 4]: a and b are the same object
print(a is b)  # True: identical objects
c = a[:]       # A shallow copy
print(a is c, a == c)  # False True: different object, equal value
