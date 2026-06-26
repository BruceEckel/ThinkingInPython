# exit_stack.py
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    print(f"open {name}")
    try:
        yield name
    finally:
        print(f"close {name}")

with ExitStack() as stack:
    names = [stack.enter_context(tag(n)) for n in ("a", "b", "c")]
    print("using", names)
## open a
## open b
## open c
## using ['a', 'b', 'c']
## close c
## close b
## close a
