# cache_speedup.py
from functools import cache

calls = 0

def fib_plain(n: int) -> int:
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)

@cache
def fib_cached(n: int) -> int:
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)

print(fib_plain(25), calls)
#: 75025 242785
print(fib_cached(25), fib_cached.cache_info().misses)
#: 75025 26
