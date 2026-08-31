# decoration_time.py
from collections.abc import Callable

def announce(func: Callable) -> Callable:
    print("Decorating")
    def wrapper() -> None:
        print("Calling")
        func()
    return wrapper

@announce
def cheese() -> None:
    print("Wensleydale")

print("Definitions done")
cheese()
#: Decorating
#: Definitions done
#: Calling
#: Wensleydale
