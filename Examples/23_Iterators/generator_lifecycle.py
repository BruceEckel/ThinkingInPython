# generator_lifecycle.py
from collections.abc import Iterator

def squares(n: int) -> Iterator[int]:
    print("first next() reached the body")
    for i in range(n):
        yield i * i

sq = squares(6)  # Body not executed
print("created")
#: created
print(next(sq))
#: first next() reached the body
#: 0
print(list(sq))  # Remainder of list
#: [1, 4, 9, 16, 25]
print(list(sq))  # Exhausted: empty, and no error
#: []
