# collect.py
from collections.abc import Generator

type Prompt = str
type Value = int
type Total = int

def collect(name: str) -> Generator[Prompt, Value, Total]:
    first: Value = yield f"{name} needs a value"
    second: Value = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")
    return first + second
