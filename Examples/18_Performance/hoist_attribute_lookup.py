# hoist_attribute_lookup.py
import timeit

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
close = abs(t_local - t_attr) < 0.2 * t_attr
print(f"hoisting made little difference: {close}")
#: hoisting made little difference: True
