# add_behavior.py
from collections.abc import Callable

def add_behavior(func: Callable) -> Callable:
    def wrapper() -> None:
        print("Some work")
        func()
        print("Some more work")

    return wrapper

@add_behavior
def cheese() -> None:
    print("Wensleydale")

cheese()
#: Some work
#: Wensleydale
#: Some more work
