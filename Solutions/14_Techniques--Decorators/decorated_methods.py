# decorated_methods.py
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

class repeat:
    def __init__(self, times: int) -> None:
        if times < 1:
            raise ValueError(
                f"times must be >= 1, got {times}")
        self.times = times

    def __call__[**P, R](
        self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            for _ in range(self.times - 1):
                result = func(*args, **kwargs)
            return result
        return wrapper

class logged:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __call__(self, *args: object,
                 **kwargs: object) -> object:
        return self.func(*args, **kwargs)

@dataclass
class Counter:
    total: int = 0

    @repeat(times=3)
    def bump(self, by: int) -> int:
        self.total += by
        return self.total

    @logged
    def peek(self) -> int:
        return self.total

counter = Counter()
print(counter.bump(2))
#: 6
bump = Counter.__dict__["bump"]
peek = Counter.__dict__["peek"]
print(type(bump).__name__, hasattr(bump, "__get__"))
#: function True
print(type(peek).__name__, hasattr(peek, "__get__"))
#: logged False
