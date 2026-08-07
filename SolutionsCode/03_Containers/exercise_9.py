# exercise_9.py

row = [1, 2, 3, 4, 5]
first, *rest = row
print(first, rest)
#: 1 [2, 3, 4, 5]
*most, last = row
print(most, last)
#: [1, 2, 3, 4] 5
first, *middle, last = row
print(first, middle, last)
#: 1 [2, 3, 4] 5
try:
    a, b = row
except ValueError as e:
    print(e)
#: too many values to unpack (expected 2, got 5)
