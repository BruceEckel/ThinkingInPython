# lazy.py
from collections.abc import Iterator
from itertools import count, islice

# A generator yields values one at a time, on demand:
def squares() -> Iterator[int]:
    for n in count(1):
        yield n * n

# count() is infinite; islice() pulls only what we ask for:
first_five = list(islice(squares(), 5))
print(first_five)
#: [1, 4, 9, 16, 25]
