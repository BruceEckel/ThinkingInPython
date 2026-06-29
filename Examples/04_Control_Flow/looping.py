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
scores = [88, 91, 79, 54, 99]  # Last one unused
for i, name, score in zip(range(10), names, scores):
    print(i, name, score)
#: 0 Alice 88
#: 1 Bob 91
#: 2 Carol 79
#: 3 Ted 54
