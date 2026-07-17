# references.py

x = 10  # x names an int
x = "ten"  # The same name now binds to a str
a = [1, 2, 3]
b = a  # b binds to the same list, not a copy
b.append(4)
print(a)  # The same object: a and b
#: [1, 2, 3, 4]
print(a is b)  # Identical objects
#: True
c = a[:]  # A shallow copy
print(a is c, a == c)  # Different object, equal value
#: False True
