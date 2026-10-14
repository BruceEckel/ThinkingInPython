# forgot_items.py

ages = {"Alice": 30, "Bob": 25}
try:
    for name, age in ages:  # [1]
        print(name, age)
except ValueError as e:
    print(e)
#: too many values to unpack (expected 2)
for name, age in {"Bo": 1, "Al": 2}:  # [2]
    print(name, age)
#: B o
#: A l
