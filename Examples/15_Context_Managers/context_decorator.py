# context_decorator.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tracing(label: str) -> Iterator[None]:
    print(f"-> {label}")
    try:
        yield
    finally:
        print(f"<- {label}")

@tracing("add")
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    with tracing("block"):
        print("inside")
    print(add(2, 3))
    print(add(10, 20))
#: -> block
#: inside
#: <- block
#: -> add
#: <- add
#: 5
#: -> add
#: <- add
#: 30
