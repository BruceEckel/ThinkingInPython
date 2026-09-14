# exercise_5.py
import sys
import tracemalloc
from collections.abc import Iterator
from itertools import islice, tee

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

N = 100_000

def peak_at_gap(k: int) -> int:
    ahead, behind = tee(squares(N))
    tracemalloc.start()
    for _ in islice(ahead, k):  # Open the gap
        pass
    for _ in zip(ahead, behind, strict=False):
        pass  # Both advance, the gap stays k
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak

near = peak_at_gap(100)
far = peak_at_gap(10_000)
if "--numbers" in sys.argv:  # Sizes on your machine
    print(f"k=100 {near:,}, k=10,000 {far:,}")
print(f"the wider gap buffers more: {far > near}")
#: the wider gap buffers more: True
