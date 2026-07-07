# functools_lru_cache.py
from functools import lru_cache

@lru_cache(maxsize=2)
def square(n: int) -> int:
    return n * n

square(1)
square(2)
square(3)  # Evicts 1, the least recently used
print(square.cache_info())
#: CacheInfo(hits=0, misses=3, maxsize=2, currsize=2)
