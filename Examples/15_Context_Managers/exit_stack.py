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

def wrap(names: list[str]) -> None:
    with ExitStack() as stack:
        open_tags = [
            stack.enter_context(tag(n)) for n in names]
        print("using", open_tags)

wrap(["a", "b"])
#: open a
#: open b
#: using ['a', 'b']
#: close b
#: close a
wrap(["a", "b", "c"])
#: open a
#: open b
#: open c
#: using ['a', 'b', 'c']
#: close c
#: close b
#: close a
