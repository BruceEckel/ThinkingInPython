# exercise_7.py
from collections.abc import Generator
from contextlib import ExitStack, contextmanager

@contextmanager
def tag(name: str) -> Generator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

def wrap(names: list[str]) -> None:
    with ExitStack() as stack:
        open_tags = [stack.enter_context(tag(n))
                     for n in names]
        print("using", open_tags)

wrap([])
#: using []
wrap(["x", "y", "z"])
#: <x>
#: <y>
#: <z>
#: using ['x', 'y', 'z']
#: </z>
#: </y>
#: </x>
