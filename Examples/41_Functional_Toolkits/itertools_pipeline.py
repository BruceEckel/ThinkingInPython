# itertools_pipeline.py
from itertools import batched, count, islice, takewhile

squares = (n * n for n in count(1))
batches = batched(squares, 3)
totals = (sum(b) for b in batches)
print(list(takewhile(lambda t: t < 500, totals)))
#: [14, 77, 194, 365]
print(list(islice(squares, 3)))
#: [256, 289, 324]
