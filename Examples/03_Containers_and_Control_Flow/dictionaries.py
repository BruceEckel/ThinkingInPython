# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages)
#: {'Alice': 30, 'Bob': 25}
print(ages["Alice"])
#: 30
ages["Carol"] = 41         # Add or update
print("Bob" in ages)       # Membership tests the keys
#: True
print(ages.get("Dan", 0))  # A default when the key is missing
#: 0
for name, age in ages.items():
    print(name, age)
#: Alice 30
#: Bob 25
#: Carol 41
