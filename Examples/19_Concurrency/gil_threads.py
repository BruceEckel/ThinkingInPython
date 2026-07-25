# gil_threads.py
from thread_compare import compare

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

orders = [1, 2, 3, 4, 5]
seq, thr = compare(cpu_price, orders, number=5)
print(f"threads no faster: {thr > seq * 0.9}")
#: threads no faster: True
