# tee.py
from itertools import tee
from typing import Final
from benchmark import report, traced

# Two independent readers, one source
a, b = tee(i * i for i in range(5))
print(list(a), list(b))
#: [0, 1, 4, 9, 16] [0, 1, 4, 9, 16]

N: Final[int] = 100_000
first, second = tee(i * i for i in range(N))
with traced() as buffered:
    for _ in first:  # Drain first; second waits
        pass
with traced() as listed:
    collected = [i * i for i in range(N)]
report(tee_bytes=buffered.current,
       list_bytes=listed.current)
print(f"tee held as much as the list: "
      f"{buffered.current > listed.current * 0.9}")
#: tee held as much as the list: True

# Same N, but both branches advance together:
first2, second2 = tee(i * i for i in range(N))
with traced() as lockstep:
    for _ in zip(first2, second2, strict=True):
        pass
report(lockstep_bytes=lockstep.peak)
print(f"lockstep buffered far less: "
      f"{lockstep.peak < listed.current * 0.1}")
#: lockstep buffered far less: True
