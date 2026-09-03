# generator_memory.py
import tracemalloc
from collections.abc import Iterator
from typing import Final
from benchmark import report

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

N: Final[int] = 1_000_000

tracemalloc.start()
total = 0
for x in squares(N):
    total += x
lazy_peak, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
collected = list(squares(N))
eager_peak, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

report(lazy_bytes=lazy_peak, eager_bytes=eager_peak)
print(f"generator used far less memory: "
      f"{lazy_peak < eager_peak * 0.01}")
#: generator used far less memory: True
