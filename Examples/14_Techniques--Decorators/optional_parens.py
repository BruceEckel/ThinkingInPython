# optional_parens.py
from collections.abc import Callable
from functools import wraps
from typing import Any, overload

type Decorator[**P, R] = Callable[
    [Callable[P, R]], Callable[P, R]]

@overload
def label[**P, R](
        func: Callable[P, R],
) -> Callable[P, R]: ...
@overload
def label[**P, R](
        func: None = None, *, prefix: str = "LOG"
) -> Decorator[P, R]: ...

def label[**P, R](
        func: Callable[P, R] | None = None,
        *, prefix: str = "LOG",
) -> Any:
    def decorate(
            f: Callable[P, R]
    ) -> Callable[P, R]:
        @wraps(f)
        def wrapper(
                *args: P.args, **kwargs: P.kwargs
        ) -> R:
            print(f"[{prefix}] {wrapper.__name__}")
            return f(*args, **kwargs)
        return wrapper
    return decorate if func is None else decorate(func)

@label
def one() -> None: ...

@label(prefix="TAG")
def two() -> None: ...

if __name__ == "__main__":
    one()
    two()
#: [LOG] one
#: [TAG] two
