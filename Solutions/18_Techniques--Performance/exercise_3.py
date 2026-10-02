# exercise_3.py
import tracemalloc
from collections.abc import Callable
from itertools import islice

n = 1_000_000

def two_lists() -> list[int]:  # The original
    squares = [x * x for x in range(n)]
    evens = [s for s in squares if s % 2 == 0]
    return evens[:5]

def one_list() -> list[int]:
    return [x * x for x in range(n) if (x * x) % 2 == 0][:5]

def lazy() -> list[int]:  # The chapter's lazy version
    squares = (x * x for x in range(n))
    evens = (s for s in squares if s % 2 == 0)
    return list(islice(evens, 5))

def peak_of(func: Callable[[], list[int]]) -> int:
    tracemalloc.start()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak

result = one_list()
print(result, result == two_lists() == lazy())
#: [0, 4, 16, 36, 64] True
two, one = peak_of(two_lists), peak_of(one_list)
print("peak ratio, one list to two:", round(one / two, 1))
#: peak ratio, one list to two: 0.5
print(f"lazy peak under 1% of one list: "
      f"{peak_of(lazy) * 100 < one}")
#: lazy peak under 1% of one list: True
