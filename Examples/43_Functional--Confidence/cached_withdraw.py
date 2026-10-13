# cached_withdraw.py
from functools import lru_cache

balance = 100

@lru_cache
def withdraw(amount: int) -> int:
    global balance
    balance -= amount
    return balance

print(withdraw(30), withdraw(30))
#: 70 70
print(f"balance: {balance}")
#: balance: 70
print(withdraw.cache_info())
#: CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
