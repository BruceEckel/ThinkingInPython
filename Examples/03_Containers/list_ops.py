# list_ops.py

xs = [10, 20, 30]
xs.append(40)  # Add one item at the end
xs.extend([50, 60])  # Add every item of an iterable
xs.insert(1, 15)  # Insert before index 1
print(xs, len(xs))
#: [10, 15, 20, 30, 40, 50, 60] 7
xs.remove(15)  # Remove the first item equal to 15
del xs[0]  # Remove by index
print(xs, 30 in xs)
#: [20, 30, 40, 50, 60] True
