# simple_decoration.py
from collections.abc import Callable

def hijack(func: Callable) -> Callable:
    def doesnt_matter() -> None:
        print("Replacement behavior")

    return doesnt_matter

@hijack
def cheese() -> None:
    print("Wensleydale")

cheese()
#: Replacement behavior
