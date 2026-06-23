# add_behavior.py
from collections.abc import Callable

def hijack(func: Callable) -> Callable:
    def doesnt_matter() -> None:
        print("Hijacked!")
        func()
        print("Hijacking over...")

    return doesnt_matter

@hijack
def cheese() -> None:
    print("Wensleydale")

cheese()
