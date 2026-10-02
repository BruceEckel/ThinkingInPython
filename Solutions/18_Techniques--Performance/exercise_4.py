# exercise_4.py
from functools import cache

@cache
def noisy(n: int) -> int:
    print(f"computing noisy({n})")
    return n * n

print(noisy(3))
#: computing noisy(3)
#: 9
print(noisy(3))
#: 9
print(noisy(3))
#: 9
