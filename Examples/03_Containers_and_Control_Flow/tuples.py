# tuples.py

point = (3, 4)
point = 3, 4        # Also a tuple; the comma is what matters
empty = ()          # Empty tuple
x, y = point        # Unpacking
print(x, y)
## 3 4
single = (42,)      # A one-element tuple needs the trailing comma
print(len(single))
## 1
print(tuple([1, 2, 3]))    # Converts to (1, 2, 3)  from a list
## (1, 2, 3)
print(tuple("abc"))
## ('a', 'b', 'c')

def min_max(values):
    return min(values), max(values)  # Returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)
## 1 9
