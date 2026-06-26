# generator_cm.py
# A one-yield generator becomes a context manager. Before yield is
# setup; after yield is teardown.
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

with tag("p") as t:
    print(f"  text in {t}")
## <p>
##   text in p
## </p>
