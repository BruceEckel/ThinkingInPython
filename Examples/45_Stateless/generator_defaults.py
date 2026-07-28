# generator_defaults.py
from collections.abc import Generator, Iterator

def countdown(n: int) -> Generator[int]:
    while n > 0:
        yield n
        n -= 1

def squares(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * i

print(list(countdown(3)), list(squares(3)))
#: [3, 2, 1] [0, 1, 4]
