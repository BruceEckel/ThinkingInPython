# membership.py
import timeit

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
target = n - 1  # Worst case: the last element in the list

t_list = timeit.timeit(lambda: target in as_list, number=100)
t_set = timeit.timeit(lambda: target in as_set, number=100)
print(f"set at least 100x faster: {t_set * 100 < t_list}")
#: set at least 100x faster: True
