# tee.py
import tracemalloc
from collections.abc import Iterator
from itertools import tee
from typing import Final
from benchmark import report

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

# Two independent readers, one source
a, b = tee(squares(5))
print(list(a), list(b))
#: [0, 1, 4, 9, 16] [0, 1, 4, 9, 16]

N: Final[int] = 100_000
first, second = tee(squares(N))
tracemalloc.start()
for _ in first:  # Drain one branch; second has not started
    pass
buffered, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
collected = list(squares(N))
listed, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()
report(tee_bytes=buffered, list_bytes=listed)
print(f"tee held as much as the list: "
      f"{buffered > listed * 0.9}")
#: tee held as much as the list: True
