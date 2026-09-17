# getattr_adapter.py
from dataclasses import dataclass
from typing import Any

class WhatIHave:
    def g(self) -> str: return "g"
    def h(self) -> str: return "h"

@dataclass(frozen=True)
class Adapter:
    adaptee: WhatIHave

    def f(self) -> str:  # The new interface
        return self.adaptee.g() + self.adaptee.h()

    # Forwards the rest
    def __getattr__(self, name: str) -> Any:
        return getattr(self.adaptee, name)

if __name__ == "__main__":
    a = Adapter(WhatIHave())
    print(a.f())  # Adapted method
    print(a.g())  # Forwarded to the adaptee unchanged
#: gh
#: g
