# optional_parens.py
from collections.abc import Callable
from functools import wraps
from typing import Any, overload

@overload
def label[**P, R](
        func: Callable[P, R],
) -> Callable[P, R]: ...
@overload
def label[**P, R](
        func: None = None, *, prefix: str = "LOG"
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

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
            print(f"[{prefix}] {f.__name__}")  # type: ignore
            return f(*args, **kwargs)
        return wrapper
    return decorate(func) if callable(func) else decorate

@label
def one() -> None: ...

@label(prefix="TAG")
def two() -> None: ...

if __name__ == "__main__":
    one()
    two()
#: [LOG] one
#: [TAG] two
