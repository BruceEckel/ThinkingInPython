# no_finally.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def careless(name: str) -> Generator[str]:
    print(f"enter {name}")
    yield name
    print(f"exit {name}")

try:
    with careless("A"):
        raise ValueError("boom")
except ValueError as error:
    print("caught:", error)
#: enter A
#: caught: boom
