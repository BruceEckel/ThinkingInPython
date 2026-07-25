# exercise_4.py
from collections.abc import Iterator
from dataclasses import dataclass

def squares(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * i

# Fix one: collect once, then reuse the list.
collected = list(squares(5))
print(collected)
#: [0, 1, 4, 9, 16]
print(collected)
#: [0, 1, 4, 9, 16]

# Fix two: an iterable whose __iter__() builds a fresh generator.
@dataclass
class Squares:
    n: int

    def __iter__(self) -> Iterator[int]:
        for i in range(self.n):
            yield i * i

sq = Squares(5)
print(list(sq))
#: [0, 1, 4, 9, 16]
print(list(sq))
#: [0, 1, 4, 9, 16]
