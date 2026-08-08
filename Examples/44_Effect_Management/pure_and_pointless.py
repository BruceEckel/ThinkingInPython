# pure_and_pointless.py
import timeit
from benchmark import report

def compute_and_discard() -> None:
    total = 0
    for i in range(2_000_000):
        total += i * i

def do_nothing() -> None:
    pass

busy = timeit.timeit(compute_and_discard, number=5)
idle = timeit.timeit(do_nothing, number=5)
report(busy_loop=busy, empty_function=idle)
print(f"burned real CPU time for nothing: {busy > idle * 100}")
#: burned real CPU time for nothing: True
