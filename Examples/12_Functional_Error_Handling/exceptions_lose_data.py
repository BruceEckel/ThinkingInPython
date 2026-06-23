# exceptions_lose_data.py

def func_a(i: int) -> int:
    if i == 1:
        raise ValueError(f"func_a({i})")
    return i

try:
    results = [func_a(i) for i in range(3)]
    print(results)
except ValueError as e:
    print(f"Lost everything: {e}")
