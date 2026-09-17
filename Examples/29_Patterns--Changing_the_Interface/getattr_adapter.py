# getattr_adapter.py
from typing import Any
from record import record

class WhatIHave:
    def g(self, n: int) -> str: return "g" * n
    def h(self, n: int) -> str: return "h" * n

@record
class Adapter:
    adaptee: WhatIHave

    def f(self, n: int) -> str:  # The new interface
        return ("f" * n +
            self.adaptee.g(n) + self.adaptee.h(n))

    # Forward the rest
    def __getattr__(self, name: str) -> Any:
        return getattr(self.adaptee, name)

if __name__ == "__main__":
    a = Adapter(WhatIHave())
    print(a.f(3))  # Adapted method
    print(a.g(5))  # Forwarded to the adaptee unchanged
    print(a.h(7))
#: fffggghhh
#: ggggg
#: hhhhhhh
