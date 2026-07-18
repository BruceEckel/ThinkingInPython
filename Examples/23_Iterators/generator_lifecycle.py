# generator_lifecycle.py
from collections.abc import Iterator

def squares(n: int) -> Iterator[int]:
    print("first next() reached the body")
    for i in range(n):
        yield i * i

sq = squares(3)  # Runs none of the body
print("created")
#: created
print(list(sq))
#: first next() reached the body
#: [0, 1, 4]
print(list(sq))  # Exhausted: empty, and no error
#: []
