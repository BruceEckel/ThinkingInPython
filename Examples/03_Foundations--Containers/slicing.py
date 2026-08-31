# slicing.py

xs = [10, 20, 30, 40, 50]
print(xs[0], xs[-1])  # First and last
#: 10 50
print(xs[1:3])  # The stop index is excluded
#: [20, 30]
print(xs[:2])  # From the start
#: [10, 20]
print(xs[2:])  # To the end
#: [30, 40, 50]
print(xs[::2])  # Every second item
#: [10, 30, 50]
print(xs[::-1])  # Reversed
#: [50, 40, 30, 20, 10]
