# manual_forwarding.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def manual() -> Generator[str, int]:
    for prompt in collect("alpha"):  # noqa: UP028
        yield prompt

g = manual()
print(next(g))
#: alpha needs a value
try:
    for value in [1, 2, 3]:
        print(g.send(value))
except StopIteration:
    print("manual() is exhausted")
#: alpha needs another
#: alpha got None and None
#: manual() is exhausted
