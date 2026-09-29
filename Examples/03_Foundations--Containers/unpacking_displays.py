# unpacking_displays.py

evens = [0, 2, 4]
odds = (1, 3)
print([*evens, *odds])  # A list from a list and a tuple
#: [0, 2, 4, 1, 3]
print((*odds, 5))  # A tuple display takes stars too
#: (1, 3, 5)
print([*"ab", *range(2)])  # Any iterable spreads
#: ['a', 'b', 0, 1]
print([*sorted("cab"), "d"])  # So does a call's result
#: ['a', 'b', 'c', 'd']
first, *rest = evens
print([*rest, first])  # Collect, then spread
#: [2, 4, 0]
