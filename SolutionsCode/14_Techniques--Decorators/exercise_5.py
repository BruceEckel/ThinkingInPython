# exercise_5.py
from collections.abc import Callable
from functools import wraps
from typing import Any, overload

@overload
def memo[**P, R](
    func: Callable[P, R]
) -> Callable[P, R]: ...

@overload
def memo[**P, R](
    *, maxsize: int = ...
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

def memo[**P, R](
    func: Callable[P, R] | None = None, *,
    maxsize: int = 128
) -> Any:
    def decorate(target: Callable[P, R]) -> Callable[P, R]:
        cache: dict[tuple[Any, ...], R] = {}

        @wraps(target)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, tuple(kwargs.items()))
            if key not in cache:
                cache[key] = target(*args, **kwargs)
                if len(cache) > maxsize:
                    del cache[next(iter(cache))]
            return cache[key]
        return wrapper
    return decorate if func is None else decorate(func)

@memo
def square(n: int) -> int:
    print(f"computing square({n})")
    return n * n

@memo(maxsize=2)
def add(a: int, b: int) -> int:
    print(f"computing add({a}, {b})")
    return a + b

print(square(4), square(4))
#: computing square(4)
#: 16 16
add(1, 2)
#: computing add(1, 2)
add(3, 4)
#: computing add(3, 4)
add(5, 6)  # A third entry, so add(1, 2) is evicted
#: computing add(5, 6)
add(5, 6)  # Still cached, so nothing prints
add(1, 2)  # Gone from the cache, so it runs again
#: computing add(1, 2)
print(square.__name__, add.__name__)
#: square add
