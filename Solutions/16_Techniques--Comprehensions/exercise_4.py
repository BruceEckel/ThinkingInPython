# exercise_4.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name.capitalize() for name in names}

print(len(unique))
#: 4
print(sorted(unique))
#: ['Alice', 'Bob', 'J', 'John']
