# tuples.py

point = (3, 4)
x, y = point        # unpacking
print(x, y)         # 3 4
single = (42,)      # a one-element tuple needs the trailing comma
print(len(single))  # 1

def min_max(values):
    return min(values), max(values)  # returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)    # 1 9
