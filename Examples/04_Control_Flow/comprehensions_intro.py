# comprehensions_intro.py

squares = [n * n for n in range(5)]  # List comprehension
print(squares)
#: [0, 1, 4, 9, 16]
# With a filter
evens = [n for n in range(10) if n % 2 == 0]
print(evens)
#: [0, 2, 4, 6, 8]
# Dict comprehension
lengths = {w: len(w) for w in ["a", "bb"]}
print(lengths)
#: {'a': 1, 'bb': 2}
parities = {n % 2 for n in range(10)}  # Set comprehension
print(parities)
#: {0, 1}
