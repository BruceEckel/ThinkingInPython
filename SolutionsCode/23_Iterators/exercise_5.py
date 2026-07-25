# exercise_5.py
import tracemalloc
from collections.abc import Iterator
from itertools import tee

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

N = 100_000

first, second = tee(squares(N))
tracemalloc.start()
for _ in zip(first, second, strict=True):  # Lockstep
    pass
lockstep, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

ahead, behind = tee(squares(N))
tracemalloc.start()
for _ in ahead:  # One branch first, as tee.py does
    pass
drained, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"lockstep under 1% of draining one: "
      f"{lockstep * 100 < drained}")
#: lockstep under 1% of draining one: True
