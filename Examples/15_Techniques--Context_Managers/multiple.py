# multiple.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

with tag("ul") as outer, tag("li") as inner:
    print(f"  {outer} then {inner}")
#: <ul>
#: <li>
#:   ul then li
#: </li>
#: </ul>
