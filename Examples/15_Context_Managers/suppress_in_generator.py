# suppress_in_generator.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def ignoring(kind: type[BaseException]) -> Iterator[None]:
    try:
        yield
    except kind as error:
        print(f"swallowed {error!r}")

with ignoring(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")
print("survived")
#: before
#: swallowed ZeroDivisionError('division by zero')
#: survived
