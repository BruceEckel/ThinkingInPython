# run_once.py
from collections.abc import Callable

def run_once[T](func: Callable[[], T]) -> T:
    return func()

@run_once
def greeting() -> str:
    return "Hello, " + "world"

if __name__ == "__main__":
    print(greeting)
    print(type(greeting).__name__)
#: Hello, world
#: str
