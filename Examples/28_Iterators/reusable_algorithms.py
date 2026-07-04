# reusable_algorithms.py
from itertools import count, islice, takewhile

numbers = count(1)  # Infinite: 1, 2, 3, ...
# Square the odd numbers, lazily, then take just the first five:
odd_squares = (n * n for n in numbers if n % 2)
print(list(islice(odd_squares, 5)))
#: [1, 9, 25, 49, 81]

# takewhile() stops as soon as its condition fails:
print(list(takewhile(lambda s: s < 50, (n * n for n in count(1)))))
#: [1, 4, 9, 16, 25, 36, 49]
