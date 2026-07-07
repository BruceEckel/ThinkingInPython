# exercise_3.py
import tracemalloc

N = 1_000_000

def eager_first_evens_comprehension():
    return [x * x for x in range(N) if (x * x) % 2 == 0][:5]

tracemalloc.start()
result = eager_first_evens_comprehension()
_, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(result)
#: [0, 4, 16, 36, 64]
