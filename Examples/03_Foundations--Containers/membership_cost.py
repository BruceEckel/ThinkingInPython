# membership_cost.py
from timeit import timeit
from benchmark import report

def scan_gap(n: int) -> float:
    items = list(range(n))
    lookup = set(items)
    missing = -1
    list_time = timeit(lambda: missing in items, number=20)
    set_time = timeit(lambda: missing in lookup, number=20)
    return list_time / set_time

small_gap = scan_gap(20_000)
large_gap = scan_gap(200_000)
report(small_n=small_gap, large_n=large_gap)
print(large_gap > small_gap)  # The gap widens
#: True
