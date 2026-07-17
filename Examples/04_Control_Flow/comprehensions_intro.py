# comprehensions_intro.py

squares = [n * n for n in range(5)]  # List comprehension
print(squares)
#: [0, 1, 4, 9, 16]
evens = [n for n in range(10) if n % 2 == 0]  # With a filter
print(evens)
#: [0, 2, 4, 6, 8]
lengths = {w: len(w) for w in ["a", "bb"]}  # Dict comprehension
print(lengths)
#: {'a': 1, 'bb': 2}
parities = {n % 2 for n in range(10)}  # Set comprehension
print(parities)
#: {0, 1}
