# multiple_assignment.py

a, b = 1, 2
a, b = b, a         # swap, no temporary needed
print(a, b)         # 2 1
first, *rest = [10, 20, 30, 40]
print(first, rest)  # 10 [20, 30, 40]
