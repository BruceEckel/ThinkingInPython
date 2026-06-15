# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages["Alice"])       # 30
ages["Carol"] = 41         # add or update
print("Bob" in ages)       # True: membership tests the keys
print(ages.get("Dan", 0))  # 0: a default when the key is missing
for name, age in ages.items():
    print(name, age)
