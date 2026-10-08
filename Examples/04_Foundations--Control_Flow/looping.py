# looping.py

for i in range(3):
    print(i, end=" ")
print()
#: 0 1 2
names = ["Alice", "Bob", "Carol", "Ted"]
for index, name in enumerate(names):
    print(index, name)
#: 0 Alice
#: 1 Bob
#: 2 Carol
#: 3 Ted
for n, name in enumerate(names, start=1):
    print(n, name)
#: 1 Alice
#: 2 Bob
#: 3 Carol
#: 4 Ted
