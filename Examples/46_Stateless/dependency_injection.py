# dependency_injection.py
from typing import Any, Final
from greeter import Console

DI_CONTAINER: Final[dict[type, Any]] = {}

def register[T](t: type[T], instance: T) -> None:
    DI_CONTAINER[t] = instance

def get[T](t: type[T]) -> T:
    return DI_CONTAINER[t]

def greet(name: str) -> None:
    console = get(Console)
    console.print(f"Hello, {name}!")

try:
    greet("Alice")
except KeyError:
    print("KeyError: no Console registered")
register(Console, Console())
greet("Alice")
#: KeyError: no Console registered
#: Hello, Alice!
