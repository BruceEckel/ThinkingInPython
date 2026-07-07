# exercise_1.py
a = [1, 2, 3]
b = a           # b is another name for the same list
b.append(4)
c = a[:]        # A shallow copy: a new list, same values
c.append(99)
print(a, c)
#: [1, 2, 3, 4] [1, 2, 3, 4, 99]
