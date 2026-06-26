# set_comprehension.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name[0].upper() + name[1:].lower()
          for name in names if len(name) > 1}
print(sorted(unique))  # Sorted for stable display
## ['Alice', 'Bob', 'John']

# set() of a list comprehension gives the same result, but builds a
# throwaway list first, so the set comprehension is preferred:
same = set([name[0].upper() + name[1:].lower()
            for name in names if len(name) > 1])
print(unique == same)
## True
