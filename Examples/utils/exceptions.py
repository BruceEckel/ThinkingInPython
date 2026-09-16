# utils/exceptions.py
import textwrap
from collections.abc import Awaitable, Callable
from typing import Final

WIDTH: Final[int] = 57
ALL = sentinel("ALL")
type Types = (type[BaseException]
              | tuple[type[BaseException], ...])

class ignore:
    def __init__(self, types: Types | ALL = ALL) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object) -> bool:
        if exc_type is None:
            return False
        if self.types is not ALL:
            if not issubclass(exc_type, self.types):
                return False
        print(textwrap.fill(f"{exc!r}", WIDTH))
        return True

def report(e: BaseException) -> None:
    line = f"[{type(e).__name__}] {e}"
    print(textwrap.fill(line, WIDTH))

def expect[**P](
    types: Types, fn: Callable[P, object],
    /, *args: P.args, **kwargs: P.kwargs
) -> None:
    try:
        fn(*args, **kwargs)
    except types as e:
        report(e)
        return
    raise AssertionError("no exception raised")

async def aexpect[**P](
    types: Types, fn: Callable[P, Awaitable[object]],
    /, *args: P.args, **kwargs: P.kwargs
) -> None:
    try:
        await fn(*args, **kwargs)
    except types as e:
        report(e)
        return
    raise AssertionError("no exception raised")
