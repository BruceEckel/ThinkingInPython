# tuples.py

point = (3, 4)
point = 3, 4        # also a tuple; the comma is what matters
empty = ()          # empty tuple
x, y = point        # unpacking
print(x, y)         # 3 4
single = (42,)      # a one-element tuple needs the trailing comma
print(len(single))  # 1
tuple([1, 2, 3])    # Converts to (1, 2, 3)  from a list
tuple("abc")        # ('a', 'b', 'c')

def min_max(values):
    return min(values), max(values)  # returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)    # 1 9
