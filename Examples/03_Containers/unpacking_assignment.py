# unpacking_assignment.py

first, *rest = [10, 20, 30, 40]
print(first, rest)  # A starred name always collects a list
#: 10 [20, 30, 40]
head, *middle, tail = "abcde"  # Any iterable unpacks
print(head, middle, tail)
#: a ['b', 'c', 'd'] e
(name, age), city = ("Alice", 30), "Rome"  # Nested targets
print(name, age, city)
#: Alice 30 Rome
values = [1, 2, 3]
try:
    x, y = values  # Without a star the counts must match
except ValueError as e:
    print(type(e).__name__)
#: ValueError
