# lazy_pipeline.py
import tracemalloc
from itertools import islice

N = 1_000_000

def eager_first_evens() -> list[int]:
    squares = [x * x for x in range(N)]
    evens = [s for s in squares if s % 2 == 0]
    return evens[:5]

def lazy_first_evens() -> list[int]:
    squares = (x * x for x in range(N))
    evens = (s for s in squares if s % 2 == 0)
    return list(islice(evens, 5))

tracemalloc.start()
eager = eager_first_evens()
_, eager_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
lazy = lazy_first_evens()
_, lazy_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(eager, eager == lazy)
#: [0, 4, 16, 36, 64] True
print(f"lazy peak under 1% of eager: {lazy_peak * 100 < eager_peak}")
#: lazy peak under 1% of eager: True
