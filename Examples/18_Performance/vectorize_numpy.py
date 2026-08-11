# vectorize_numpy.py
import timeit
import numpy as np
from benchmark import report

n = 1_000_000
numbers = list(range(n))
a = np.arange(n, dtype=np.float64)

def pure_python() -> list[float]:
    return [3.0 * x + 1.0 for x in numbers]

def vectorized() -> np.ndarray:
    return 3.0 * a + 1.0

t_loop = timeit.timeit(pure_python, number=5)
t_numpy = timeit.timeit(vectorized, number=5)
report(python_loop=t_loop, numpy=t_numpy, ratio=t_loop / t_numpy)
print(f"NumPy at least 3x faster: {t_numpy * 3 < t_loop}")
#: NumPy at least 3x faster: True
