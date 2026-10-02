# exercise_8.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def careful(name: str) -> Iterator[str]:
    print(f"enter {name}")
    try:
        yield name
    finally:
        print(f"exit {name}")

try:
    with careful("A"):
        raise ValueError("boom")
except ValueError as error:
    print("caught:", error)
#: enter A
#: exit A
#: caught: boom
