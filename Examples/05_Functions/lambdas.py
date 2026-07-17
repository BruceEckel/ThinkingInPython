# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=lambda w: len(w)))  # Sort by length
#: ['fig', 'kiwi', 'apple', 'banana']
square = lambda n: n * n  # Usually prefer def
print(square(9))
#: 81
