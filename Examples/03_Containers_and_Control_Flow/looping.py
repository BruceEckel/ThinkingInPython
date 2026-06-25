# looping.py

for i in range(3):
    print(i, end=" ")
print()
## 0 1 2
names = ["Alice", "Bob", "Carol"]
for index, name in enumerate(names):
    print(index, name)
## 0 Alice
## 1 Bob
## 2 Carol
scores = [88, 91, 79]
for name, score in zip(names, scores):
    print(name, score)
## Alice 88
## Bob 91
## Carol 79
