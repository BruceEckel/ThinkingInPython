# tee.py
import tracemalloc
from itertools import tee
from typing import Final
from benchmark import report

# Two independent readers, one source
a, b = tee(i * i for i in range(5))
print(list(a), list(b))
#: [0, 1, 4, 9, 16] [0, 1, 4, 9, 16]

N: Final[int] = 100_000
first, second = tee(i * i for i in range(N))
tracemalloc.start()
for _ in first:  # Drain one branch; second has not started
    pass
buffered, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
collected = [i * i for i in range(N)]
listed, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()
report(tee_bytes=buffered, list_bytes=listed)
print(f"tee held as much as the list: "
      f"{buffered > listed * 0.9}")
#: tee held as much as the list: True

# Same N, but both branches advance together:
first2, second2 = tee(i * i for i in range(N))
tracemalloc.start()
for _ in zip(first2, second2, strict=True):
    pass
_, lockstep = tracemalloc.get_traced_memory()
tracemalloc.stop()
report(lockstep_bytes=lockstep)
print(f"lockstep buffered far less: "
      f"{lockstep < listed * 0.1}")
#: lockstep buffered far less: True
