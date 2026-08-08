# membership_cost.py
from timeit import timeit
from benchmark import report

n = 200_000
items = list(range(n))
lookup = set(items)
missing = -1
list_time = timeit(lambda: missing in items, number=20)
set_time = timeit(lambda: missing in lookup, number=20)
report(list_scan=list_time, set_lookup=set_time)
print(set_time * 100 < list_time)  # Not close
#: True
