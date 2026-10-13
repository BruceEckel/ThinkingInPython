# collatz_numba.py
import timeit
import numpy as np
from benchmark import report
from numba import njit

def collatz_lengths(values: np.ndarray) -> np.ndarray:
    lengths = np.empty(len(values), dtype=np.int64)
    for i in range(len(values)):
        n = int(values[i])
        steps = 0
        while n != 1:
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            steps += 1
        lengths[i] = steps
    return lengths

fast_collatz_lengths = njit(collatz_lengths)
values = np.arange(1, 50_000, dtype=np.int64)
sample = values[:100]
assert np.array_equal(
    fast_collatz_lengths(sample), collatz_lengths(sample))
t_python = timeit.timeit(
    lambda: collatz_lengths(values), number=1)
t_numba = timeit.timeit(
    lambda: fast_collatz_lengths(values), number=1)
report(python_loop=t_python, numba=t_numba,
       ratio=t_python / t_numba)
print(f"Numba at least 3x faster: {t_numba * 3 < t_python}")
#: Numba at least 3x faster: True
