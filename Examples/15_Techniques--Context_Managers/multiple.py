# multiple.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Generator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

if __name__ == "__main__":
    with tag("ul") as outer, tag("li") as inner:
        print(f"  {outer} then {inner}")
#: <ul>
#: <li>
#:   ul then li
#: </li>
#: </ul>
