# exercise_2.py
import time
from collections.abc import Callable
from functools import wraps

def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"-> {func.__name__}{args}")  # type: ignore
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} = {result!r}")  # type: ignore
        return result
    return wrapper

def timing[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        # elapsed differs every run: print a fixed message plus a
        # deterministic check, not the raw, ever-changing number.
        ok = elapsed >= 0
        name = func.__name__  # type: ignore
        print(f"{name} timed, non-negative: {ok}")
        return result
    return wrapper

@trace
@timing
def add(a: int, b: int) -> int:
    return a + b

add(2, 3)
#: -> add(2, 3)
#: add timed, non-negative: True
#: <- add = 5
