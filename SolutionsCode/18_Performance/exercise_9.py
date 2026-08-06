# exercise_9.py
import timeit
from array import array

n = 200_000
as_list = [float(i) for i in range(n)]
as_array = array("d", as_list)

def best(f: object) -> float:
    return min(timeit.repeat(f, number=20, repeat=5))  # type: ignore

t_list = best(lambda: sum(as_list))
t_array = best(lambda: sum(as_array))
print(f"array is slower to iterate: {t_array > t_list}")
#: array is slower to iterate: True
