# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=lambda w: len(w)))  # sort by length
square = lambda n: n * n                     # usually prefer def
print(square(9))                             # 81
