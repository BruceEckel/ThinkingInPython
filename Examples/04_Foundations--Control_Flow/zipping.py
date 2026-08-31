# zipping.py

names = ["Alice", "Bob", "Carol", "Ted"]
scores = [88, 91, 79, 54, 99]  # One score too many
for name, score in zip(names, scores):
    print(name, score)
#: Alice 88
#: Bob 91
#: Carol 79
#: Ted 54
try:
    list(zip(names, scores, strict=True))
except ValueError as e:
    print(e)
#: zip() argument 2 is longer than argument 1
