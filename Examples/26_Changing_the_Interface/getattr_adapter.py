# getattr_adapter.py
# The usual adapter need: forward most calls, change a few.
# __getattr__ delegates everything you do not override, so the
# wrapper stays small.
from typing import Any

class WhatIHave:
    def g(self) -> str: return "g"
    def h(self) -> str: return "h"

class Adapter:
    def __init__(self, adaptee: WhatIHave) -> None:
        self._adaptee = adaptee

    def f(self) -> str:                       # The new interface
        return self._adaptee.g() + self._adaptee.h()

    def __getattr__(self, name: str) -> Any:  # Forwards the rest
        return getattr(self._adaptee, name)

a = Adapter(WhatIHave())
print(a.f())   # Adapted method
## gh
print(a.g())   # Forwarded to the adaptee unchanged
## g
