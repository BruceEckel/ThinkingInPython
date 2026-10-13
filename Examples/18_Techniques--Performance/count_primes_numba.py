# count_primes_numba.py
import timeit
from benchmark import report
from numba import njit

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        for d in range(2, int(n**0.5) + 1):
            if n % d == 0:
                break
        else:
            count += 1
    return count

fast_count_primes = njit(count_primes)
assert fast_count_primes(1_000) == count_primes(1_000)
limit = 200_000
t_python = timeit.timeit(
    lambda: count_primes(limit), number=1)
t_numba = timeit.timeit(
    lambda: fast_count_primes(limit), number=1)
report(python_loop=t_python, numba=t_numba,
       ratio=t_python / t_numba)
print(f"Numba at least 3x faster: {t_numba * 3 < t_python}")
#: Numba at least 3x faster: True
