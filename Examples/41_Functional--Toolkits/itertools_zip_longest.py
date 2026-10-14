# itertools_zip_longest.py
from itertools import zip_longest
from exceptions import expect

print(list(zip_longest([1, 2, 3], [4, 5])))
#: [(1, 4), (2, 5), (3, None)]

MISSING = sentinel("MISSING")
print(list(zip_longest([1, 2, 3], [4, 5],
                       fillvalue=MISSING)))
#: [(1, 4), (2, 5), (3, MISSING)]
print(list(zip([1, 2, 3], [4, 5])))  # [1]
#: [(1, 4), (2, 5)]
expect(ValueError, list,  # [2]
       zip([1, 2, 3], [4, 5], strict=True))
#: [ValueError] zip() argument 2 is shorter than argument 1
