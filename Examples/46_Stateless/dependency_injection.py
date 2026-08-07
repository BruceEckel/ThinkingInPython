# dependency_injection.py
from typing import Any, Final
from greeter import Console

class NotRegistered(Exception):
    pass

DI_CONTAINER: Final[dict[type, Any]] = {}

def register[T](t: type[T], instance: T) -> None:
    DI_CONTAINER[t] = instance

def get[T](t: type[T]) -> T:
    try:
        return DI_CONTAINER[t]
    except KeyError as e:
        raise NotRegistered(t.__name__) from e

def greet(name: str) -> None:
    console: Console = get(Console)
    console.print(f"Hello, {name}!")

try:
    greet("Alice")
except NotRegistered as e:
    print(f"{type(e).__name__}: {e}")
#: NotRegistered: Console
register(Console, Console())
greet("Alice")
#: Hello, Alice!
