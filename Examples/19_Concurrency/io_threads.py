# io_threads.py
import time
import timeit
from concurrent.futures import ThreadPoolExecutor

def io_price(order: int) -> int:
    time.sleep(0.05)  # Waiting outside the processor
    return order * 10

def sequential(orders: list[int]) -> list[int]:
    return [io_price(o) for o in orders]

def threaded(orders: list[int]) -> list[int]:
    with ThreadPoolExecutor() as pool:
        return list(pool.map(io_price, orders))

orders = [1, 2, 3, 4, 5]
assert threaded(orders) == sequential(orders)
t_seq = timeit.timeit(lambda: sequential(orders), number=1)
t_thr = timeit.timeit(lambda: threaded(orders), number=1)
print(f"threads at least 3x faster on I/O: {t_thr * 3 < t_seq}")
#: threads at least 3x faster on I/O: True
