# exit_stack_fails.py
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

@contextmanager
def tag(name: str, fail: bool = False) -> Iterator[str]:
    print(f"open {name}")
    if fail:
        raise RuntimeError(f"{name} failed to open")
    try:
        yield name
    finally:
        print(f"close {name}")

try:
    with ExitStack() as stack:
        stack.enter_context(tag("a"))
        stack.enter_context(tag("b"))
        stack.enter_context(tag("c", fail=True))
except RuntimeError as error:
    print("caught:", error)
#: open a
#: open b
#: open c
#: close b
#: close a
#: caught: c failed to open
