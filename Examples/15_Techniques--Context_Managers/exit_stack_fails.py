# exit_stack_fails.py
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from exceptions import expected
from multiple import tag

@contextmanager
def broken(name: str) -> Generator[str]:
    print(f"<{name}>")
    raise RuntimeError(f"{name} failed to open")
    yield name

with expected(RuntimeError):
    with ExitStack() as stack:
        stack.enter_context(tag("a"))
        stack.enter_context(tag("b"))
        stack.enter_context(broken("c"))
#: <a>
#: <b>
#: <c>
#: </b>
#: </a>
#: [RuntimeError] c failed to open
