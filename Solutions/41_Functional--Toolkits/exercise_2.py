# exercise_2.py
from functools import lru_cache

@lru_cache(maxsize=3)
def square(n: int) -> int:
    print(f"computing {n}")
    return n * n

square(1)
#: computing 1
square(2)
#: computing 2
square(3)
#: computing 3
square(2)
square(1)
print(square.cache_info())
#: CacheInfo(hits=2, misses=3, maxsize=3, currsize=3)
