# getattr_adapter.py
from typing import Any

class WhatIHave:
    def g(self) -> str: return "g"
    def h(self) -> str: return "h"

class Adapter:
    def __init__(self, adaptee: WhatIHave) -> None:
        self._adaptee = adaptee

    def f(self) -> str:  # The new interface
        return self._adaptee.g() + self._adaptee.h()

    # Forwards the rest
    def __getattr__(self, name: str) -> Any:
        return getattr(self._adaptee, name)

if __name__ == "__main__":
    a = Adapter(WhatIHave())
    print(a.f())  # Adapted method
    print(a.g())  # Forwarded to the adaptee unchanged
#: gh
#: g
