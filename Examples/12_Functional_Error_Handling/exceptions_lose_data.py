# exceptions_lose_data.py

def func_a(i: int) -> int:
    print(f"Calculating func_a({i})")
    if i == 3:
        raise ValueError(f"func_a({i})")
    return i

try:
    results = [func_a(i) for i in range(5)]
    print(results)
except ValueError as e:
    print(f"Lost everything: {e}")
## Calculating func_a(0)
## Calculating func_a(1)
## Calculating func_a(2)
## Calculating func_a(3)
## Lost everything: func_a(3)
