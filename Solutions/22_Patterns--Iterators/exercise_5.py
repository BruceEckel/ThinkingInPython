# exercise_5.py
from collections.abc import Iterator
from itertools import islice, tee
from typing import Final
from benchmark import report, traced

def squares(n: int) -> Iterator[int]:
    return (i * i for i in range(n))

N: Final[int] = 100_000

def peak_at_gap(k: int) -> int:
    ahead, behind = tee(squares(N))
    with traced() as memory:
        for _ in islice(ahead, k):  # Open the gap
            pass
        for _ in zip(ahead, behind, strict=False):
            pass  # Both advance, the gap stays k
    return memory.peak

near = peak_at_gap(100)
far = peak_at_gap(10_000)
report(gap_100=near, gap_10_000=far)
print(f"the wider gap buffers more: {far > near}")
#: the wider gap buffers more: True
