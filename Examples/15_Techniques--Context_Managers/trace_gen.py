# trace_gen.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def trace(name: str) -> Generator[str]:
    print(f"enter {name}")  # Setup
    try:
        yield name  # The block runs here
    finally:
        print(f"exit {name}")  # Cleanup

if __name__ == "__main__":
    with trace("A") as t:
        print(f"inside {t}")
    manager = trace("B")
    with manager:
        pass
    try:
        with manager:  # [1]
            pass
    except AttributeError as error:
        print(error)
#: enter A
#: inside A
#: exit A
#: enter B
#: exit B
#: '_GeneratorContextManager' object has no attribute 'args'
