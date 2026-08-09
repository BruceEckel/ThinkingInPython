# utils/safe.py
from collections.abc import Callable
from functools import wraps
from result import Err, Ok, Result

def safe[**P, A](
    func: Callable[P, A],
) -> Callable[P, Result[A, Exception]]:
    @wraps(func)
    def wrapper(
        *args: P.args, **kwargs: P.kwargs
    ) -> Result[A, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)
    return wrapper
