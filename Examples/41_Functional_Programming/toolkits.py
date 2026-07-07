# toolkits.py
from functools import lru_cache, reduce
from operator import add

# reduce() folds a sequence down to a single value:
print(reduce(add, [1, 2, 3, 4]))
#: 10
# lru_cache remembers results, so repeats are free:
@lru_cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(30))
#: 832040
