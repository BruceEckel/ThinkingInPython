# collect.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int, int]:
    first: int = yield f"{name} needs a value"
    second: int = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")
    return first + second
