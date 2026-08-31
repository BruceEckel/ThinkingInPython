# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages)
#: {'Alice': 30, 'Bob': 25}
print(ages["Alice"])
#: 30
ages["Carol"] = 41  # Add or update
print("Bob" in ages)  # Membership tests the keys
#: True
# A default when the key is missing
print(ages.get("Dan", 0))
#: 0
print(list(ages))  # Iterating a dict yields its keys
#: ['Alice', 'Bob', 'Carol']
print(list(ages.values()))
#: [30, 25, 41]
for name, age in ages.items():
    print(name, age)
#: Alice 30
#: Bob 25
#: Carol 41
