# walked_twice.py
from collections.abc import Collection, Iterable, Iterator

def gen(n: int) -> Iterator[int]:
    yield from range(n)

def twice_iterable(xs: Iterable[int]) -> tuple[int, int]:
    return sum(xs), sum(xs)

def twice_collection(
    xs: Collection[int]
) -> tuple[int, int]:
    return sum(xs), sum(xs)

# Type checker sees nothing wrong
print(twice_iterable(gen(3)))
#: (3, 0)
# The same values, in a list
print(twice_collection([0, 1, 2]))
#: (3, 3)
