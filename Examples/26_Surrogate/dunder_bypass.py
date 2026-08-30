# dunder_bypass.py
from typing import Any

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy(Words())
print(p.__len__())  # The explicit call delegates
#: 2
try:
    # Special-method lookup skips the instance:
    len(p)  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
print("Proxy object at" in str(p))
#: True
