# membership.py
import timeit
from benchmark import report

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
target = n - 1  # Worst case: the last element in the list

t_list = timeit.timeit(lambda: target in as_list, number=100)
t_set = timeit.timeit(lambda: target in as_set, number=100)
report(list_scan=t_list, set_lookup=t_set, ratio=t_list / t_set)
print(f"set at least 100x faster: {t_set * 100 < t_list}")
#: set at least 100x faster: True
