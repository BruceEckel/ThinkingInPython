# collect.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")
    return first + second
