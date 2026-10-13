# gil_threads.py
from benchmark import report
from pricing import cpu_price
from thread_compare import compare

orders = [1, 2, 3, 4, 5]
seq, thr = compare(cpu_price, orders, number=5)
report(sequential=seq, threaded=thr)
print(f"threads no faster: {thr > seq * 0.9}")
#: threads no faster: True
