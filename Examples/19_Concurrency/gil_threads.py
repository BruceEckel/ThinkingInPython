# gil_threads.py
import timeit
from concurrent.futures import ThreadPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    return order * 10

def sequential(orders: list[int]) -> list[int]:
    return [cpu_price(o) for o in orders]

def threaded(orders: list[int]) -> list[int]:
    with ThreadPoolExecutor() as pool:
        return list(pool.map(cpu_price, orders))

orders = [1, 2, 3, 4, 5]
assert threaded(orders) == sequential(orders)

t_seq = timeit.timeit(lambda: sequential(orders), number=5)
t_thr = timeit.timeit(lambda: threaded(orders), number=5)
print(f"threads no faster: {t_thr > t_seq * 0.9}")
#: threads no faster: True
