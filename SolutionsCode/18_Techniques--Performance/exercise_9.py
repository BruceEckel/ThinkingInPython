# exercise_9.py
import timeit
from array import array
from collections.abc import Callable
from benchmark import report

n = 200_000
as_list = [float(i) for i in range(n)]
as_array = array("d", as_list)

def best(f: Callable[[], float]) -> float:
    return min(timeit.repeat(f, number=20, repeat=5))

t_list = best(lambda: sum(as_list))
t_array = best(lambda: sum(as_array))
report(list=t_list, array=t_array)
print(f"array is slower to iterate: {t_array > t_list}")
#: array is slower to iterate: True
