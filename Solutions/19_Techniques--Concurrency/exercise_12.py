# exercise_12.py
import os
import timeit
from concurrent.futures import ThreadPoolExecutor
from benchmark import report
from pricing import Price, cpu_price

def sequential(orders: list[int]) -> list[Price]:
    return [cpu_price(o) for o in orders]

orders = [1, 2, 3, 4, 5]
t_seq = timeit.timeit(lambda: sequential(orders), number=5)

with ThreadPoolExecutor() as pool:
    parallel = list(pool.map(cpu_price, orders))
    assert parallel == sequential(orders)
    t_thr = timeit.timeit(
        lambda: list(pool.map(cpu_price, orders)), number=5
    )

cores = os.cpu_count() or 1
target = min(1.5, cores * 0.7)  # Lower on one or two cores
report(sequential=t_seq, threads=t_thr, cores=cores)
print(f"threads run in parallel: {t_seq > t_thr * target}")
#: threads run in parallel: False
