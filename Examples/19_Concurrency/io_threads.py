# io_threads.py
import time
from thread_compare import compare

def io_price(order: int) -> int:
    time.sleep(0.05)  # Stand-in for I/O
    return order * 10

orders = [1, 2, 3, 4, 5]
t_seq, t_thr = compare(io_price, orders, number=1)
print(f"threads at least 3x faster on I/O: {t_thr * 3 < t_seq}")
#: threads at least 3x faster on I/O: True
