# io_threads.py
import time
from benchmark import report
from thread_compare import compare

def io_price(order: int) -> int:
    time.sleep(0.05)  # Stand-in for I/O
    return order * 10

orders = [1, 2, 3, 4, 5]
times = compare(io_price, orders, number=1)
report(sequential=times.sequential, threaded=times.threaded)
print("threads at least 3x faster on I/O: "
      f"{times.threaded * 3 < times.sequential}")
#: threads at least 3x faster on I/O: True
