# add_behavior.py
from collections.abc import Callable

def hijack(func: Callable) -> Callable:
    def wrapper() -> None:
        print("Hijacked!")
        func()
        print("Hijacking complete...")

    return wrapper

@hijack
def cheese() -> None:
    print("Wensleydale")

cheese()
#: Hijacked!
#: Wensleydale
#: Hijacking complete...
