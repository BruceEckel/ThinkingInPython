# tuples.py

point = (3, 4)
point = 3, 4  # Also a tuple; the comma matters
empty = ()
x, y = point  # Unpacking
print(x, y)
#: 3 4
# A one-element tuple needs the trailing comma
number = (42)
single = (42,)
print(type(number).__name__, type(single).__name__)
#: int tuple
print(tuple([1, 2, 3]))
#: (1, 2, 3)
print(tuple("abc"))
#: ('a', 'b', 'c')

def min_max(values):
    return min(values), max(values)  # Returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)
#: 1 9
