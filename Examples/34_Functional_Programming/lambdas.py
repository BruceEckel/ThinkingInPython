# lambdas.py
# A lambda is an unnamed function written as one expression:
print((lambda n: n * n)(6))
#: 36
# Most often a lambda is an inline argument:
pairs = [(3, "c"), (1, "a"), (2, "b")]
pairs.sort(key=lambda pair: pair[0])
print(pairs)
#: [(1, 'a'), (2, 'b'), (3, 'c')]
# Binding a lambda to a name works, but a def is clearer:
square = lambda n: n * n
print(square(5))
#: 25
