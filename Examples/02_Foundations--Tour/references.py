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
c = a[:]  # Copies the list, not its contents
print(a is c, a == c)  # Different object, equal value
#: False True
nested = [[1], [2, 3]]
shallow = nested[:]
shallow[1].append(99)
print(nested)  # The inner list is shared
#: [[1], [2, 3, 99]]
