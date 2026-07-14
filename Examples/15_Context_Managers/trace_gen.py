# trace_gen.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def trace(name: str) -> Iterator[str]:
    print(f"enter {name}")  # Setup
    try:
        yield name  # The block runs here
    finally:
        print(f"exit {name}")  # Cleanup

if __name__ == "__main__":
    with trace("A") as t:
        print(f"inside {t}")
#: enter A
#: inside A
#: exit A
