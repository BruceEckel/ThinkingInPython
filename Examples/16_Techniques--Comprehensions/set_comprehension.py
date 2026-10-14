# set_comprehension.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name.capitalize()
          for name in names if len(name) > 1}

print(sorted(unique))  # Sorted for stable display
#: ['Alice', 'Bob', 'John']

same = set([name.capitalize()
            for name in names if len(name) > 1])

print(unique == same)
#: True
