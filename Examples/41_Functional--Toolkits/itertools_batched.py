# itertools_batched.py
from itertools import batched
from exceptions import expect

print(list(batched(range(7), 3)))
#: [(0, 1, 2), (3, 4, 5), (6,)]
expect(ValueError, list, batched(range(7), 3, strict=True))
#: [ValueError] batched(): incomplete batch
