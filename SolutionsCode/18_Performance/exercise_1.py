# exercise_1.py
import random
import timeit

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
random.seed(1)
targets = [random.randrange(n) for _ in range(200)]

def list_lookups():
    for t in targets:
        t in as_list

def set_lookups():
    for t in targets:
        t in as_set

t_list = timeit.timeit(list_lookups, number=20)
t_set = timeit.timeit(set_lookups, number=20)
print(f"set faster on average-case targets too: {t_set < t_list}")
#: set faster on average-case targets too: True
