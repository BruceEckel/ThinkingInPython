# subinterpreters.py
import os
import timeit
from concurrent.futures import InterpreterPoolExecutor
from benchmark import report

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

def sequential(orders: list[int]) -> list[int]:
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
target = min(1.5, cores * 0.7)  # Two cores cannot give 1.5x
report(sequential=t_seq, subinterpreters=t_sub, cores=cores)
print(f"subinterpreters run in parallel: {t_seq > t_sub * target}")
#: subinterpreters run in parallel: True
