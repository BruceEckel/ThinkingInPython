# search_comparison.py
import bisect
import timeit

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
target = n // 2

def scan() -> bool:
    return target in as_list

def binary_search() -> bool:
    i = bisect.bisect_left(as_list, target)
    return i < len(as_list) and as_list[i] == target

def hashed() -> bool:
    return target in as_set

assert {scan(), binary_search(), hashed()} == {True}
t_scan = timeit.timeit(scan, number=1000)
t_search = timeit.timeit(binary_search, number=1000)
t_hashed = timeit.timeit(hashed, number=1000)
print(f"binary search at least 100x faster than scan: "
      f"{t_search * 100 < t_scan}")
#: binary search at least 100x faster than scan: True
print(f"hashing at least 3x faster than binary search: "
      f"{t_hashed * 3 < t_search}")
#: hashing at least 3x faster than binary search: True
