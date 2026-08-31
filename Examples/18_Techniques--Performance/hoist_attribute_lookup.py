# hoist_attribute_lookup.py
import timeit
from benchmark import report

n = 100_000

def with_attribute_lookup() -> list[int]:
    out: list[int] = []
    for i in range(n):
        out.append(i)
    return out

def with_hoisted_local() -> list[int]:
    out: list[int] = []
    append = out.append
    for i in range(n):
        append(i)
    return out

assert with_attribute_lookup() == with_hoisted_local()
t_attr = timeit.timeit(with_attribute_lookup, number=100)
t_local = timeit.timeit(with_hoisted_local, number=100)
report(attribute_lookup=t_attr, hoisted_local=t_local)
print(f"hoisting did not halve the time: "
      f"{t_local * 2 > t_attr}")
#: hoisting did not halve the time: True
