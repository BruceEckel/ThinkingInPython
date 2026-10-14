# functools_lru_cache.py
from functools import lru_cache

@lru_cache(maxsize=2)
def square(n: int) -> int:
    print(f"computing {n}")
    return n * n

square(1)
#: computing 1
square(2)
#: computing 2
square(3)  # Evicts 1, the least recently used
#: computing 3
square(2)  # [1]
square(1)  # [2]
#: computing 1
print(square.cache_info())
#: CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)
