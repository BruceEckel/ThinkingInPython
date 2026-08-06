# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=len))
#: ['fig', 'kiwi', 'apple', 'banana']
print(sorted(words, key=lambda w: w[-1]))
#: ['banana', 'apple', 'fig', 'kiwi']
square = lambda n: n * n  # Usually prefer def
print(square(9))
#: 81
