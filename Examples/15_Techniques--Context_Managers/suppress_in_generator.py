# suppress_in_generator.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def ignoring(kind: type[BaseException]) -> Generator[None]:
    try:
        yield
    except kind as error:
        print(f"swallowed {error!r}")

with ignoring(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")
#: before
#: swallowed ZeroDivisionError('division by zero')
print("survived")
#: survived
