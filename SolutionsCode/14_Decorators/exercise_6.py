# exercise_6.py
from collections.abc import Callable
from functools import wraps

def retry[**P, R](
        times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"attempt {attempt} failed: {e}")
            return func(*args, **kwargs)
        return wrapper
    return decorate

attempts = 0

@retry(times=3)
def flaky() -> str:
    global attempts
    attempts += 1
    if attempts < 3:
        raise ValueError(f"not yet ({attempts})")
    return "succeeded"

print(flaky())
#: attempt 1 failed: not yet (1)
#: attempt 2 failed: not yet (2)
#: succeeded
print(flaky.__name__)
#: flaky

@retry(times=2)
def always_fails() -> str:
    raise RuntimeError("no luck")

try:
    always_fails()
except RuntimeError as e:
    print("escaped:", e)
#: attempt 1 failed: no luck
#: escaped: no luck
