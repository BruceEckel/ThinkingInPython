# lazy.py
from collections.abc import Iterator
from itertools import count, islice

def squares() -> Iterator[int]:
    for n in count(1):
        print(f"computing square {n}")  # Proves this runs on demand
        yield n * n

# count() is infinite; islice() pulls only what we ask for:
first_five = list(islice(squares(), 5))
print(first_five)
#: computing square 1
#: computing square 2
#: computing square 3
#: computing square 4
#: computing square 5
#: [1, 4, 9, 16, 25]
