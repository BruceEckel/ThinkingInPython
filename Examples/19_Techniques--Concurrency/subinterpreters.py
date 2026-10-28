# subinterpreters.py
import os
import timeit
from concurrent.futures import InterpreterPoolExecutor
from benchmark import report
from pricing import Price, cpu_price

def sequential(orders: list[int]) -> list[Price]:
    return [cpu_price(o) for o in orders]

orders = [1, 2, 3, 4, 5]
t_seq = timeit.timeit(lambda: sequential(orders), number=5)

with InterpreterPoolExecutor() as pool:
    parallel = list(pool.map(cpu_price, orders))
    assert parallel == sequential(orders)
    t_sub = timeit.timeit(
        lambda: list(pool.map(cpu_price, orders)), number=5
    )

cores = os.cpu_count() or 1
target = min(1.5, cores * 0.7)  # Lower on one or two cores
report(sequential=t_seq, subinterpreters=t_sub, cores=cores)
print(f"subinterpreters run in parallel: "
      f"{t_seq > t_sub * target}")
#: subinterpreters run in parallel: True
