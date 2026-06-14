# exceptions_lose_data.py
# An exception unwinds the whole computation. Partial results are thrown away:
# func_a(0) succeeded, but its result is gone.


def func_a(i: int) -> int:
    if i == 1:
        raise ValueError(f"func_a({i})")
    return i


try:
    results = [func_a(i) for i in range(3)]
    print(results)
except ValueError as e:
    print(f"Lost everything: {e}")
