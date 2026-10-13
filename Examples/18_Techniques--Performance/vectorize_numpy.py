# vectorize_numpy.py
import timeit
import numpy as np
from benchmark import report

n = 1_000_000
as_list = list(range(n))
as_array = np.arange(n, dtype=np.float64)

def pure_python() -> list[float]:
    return [3.0 * x + 1.0 for x in as_list]

def vectorized() -> np.ndarray:
    return 3.0 * as_array + 1.0

assert vectorized().tolist() == pure_python()
t_loop = timeit.timeit(pure_python, number=5)
t_numpy = timeit.timeit(vectorized, number=5)
report(python_loop=t_loop, numpy=t_numpy,
       ratio=t_loop / t_numpy)
print(f"NumPy at least 3x faster: {t_numpy * 3 < t_loop}")
#: NumPy at least 3x faster: True
