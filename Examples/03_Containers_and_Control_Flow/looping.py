# looping.py

for i in range(3):  # 0, 1, 2
    print(i, end=" ")
print()
names = ["Alice", "Bob", "Carol"]
for index, name in enumerate(names):
    print(index, name)
scores = [88, 91, 79]
for name, score in zip(names, scores):
    print(name, score)
