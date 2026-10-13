# exit_stack_fails.py
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from exceptions import expected
from exit_stack import tag

@contextmanager
def broken(name: str) -> Generator[str]:
    print(f"open {name}")
    raise RuntimeError(f"{name} failed to open")
    yield name

with expected(RuntimeError):
    with ExitStack() as stack:
        stack.enter_context(tag("a"))
        stack.enter_context(tag("b"))
        stack.enter_context(broken("c"))
#: open a
#: open b
#: open c
#: close b
#: close a
#: [RuntimeError] c failed to open
