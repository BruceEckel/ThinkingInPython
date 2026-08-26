# exercise_7.py
from typing import Any

def methods(obj: object) -> set[str]:
    return {
        name
        for name in dir(obj)
        if not name.startswith("_")
        and callable(getattr(obj, name))
    }

class Surrogate:
    def __init__(self, implementation: Any) -> None:
        self.__implementation = implementation

    def change_to(self, new: Any) -> None:
        missing = (methods(self.__implementation)
                   - methods(new))
        if missing:
            raise TypeError(f"missing: {sorted(missing)}")
        self.__implementation = new

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Full:
    def f(self) -> None: print("Full.f()")
    def g(self) -> None: print("Full.g()")

class Lacking:
    def f(self) -> None: print("Lacking.f()")

s = Surrogate(Full())
s.f()
#: Full.f()
try:
    s.change_to(Lacking())
except TypeError as e:
    print(type(e).__name__, e)
#: TypeError missing: ['g']
s.g()  # The old implementation is still in place
#: Full.g()
