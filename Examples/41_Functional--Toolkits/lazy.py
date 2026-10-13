# lazy.py
from collections.abc import Iterator
from itertools import count, islice

def squares() -> Iterator[int]:
    for n in count(1):
        # Proves this runs on demand
        print(f"computing square {n}")
        yield n * n

# count() is infinite; islice() pulls only what's needed:
for sq in islice(squares(), 3):
    print("got", sq)
#: computing square 1
#: got 1
#: computing square 2
#: got 4
#: computing square 3
#: got 9
