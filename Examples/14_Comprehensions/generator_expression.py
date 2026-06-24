# generator_expression.py
from itertools import islice

squares = (n ** 2 for n in range(1_000_000))
print(next(squares))  # 0
print(next(squares))  # 1
print(list(islice(squares, 3)))  # [4, 9, 16]
