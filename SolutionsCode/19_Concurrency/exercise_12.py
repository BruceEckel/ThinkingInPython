# exercise_12.py
import os
import sys
import timeit
from concurrent.futures import ThreadPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

def sequential(orders: list[int]) -> list[int]:
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
# The chapter's scaled target
target = min(1.5, cores * 0.7)
if "--numbers" in sys.argv:  # Exact times on your machine
    print(f"sequential {t_seq:.6f}, threaded {t_thr:.6f}")
print(f"threads run in parallel: {t_seq > t_thr * target}")
#: threads run in parallel: False
