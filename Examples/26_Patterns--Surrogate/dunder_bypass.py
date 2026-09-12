# dunder_bypass.py
from typing import Any
from exceptions import expect

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

p = Proxy(Words())
print(p.__len__())  # The explicit call delegates
#: 2
# Special-method lookup skips the instance:
expect(TypeError, len, p)  # type: ignore
#: [TypeError] object of type 'Proxy' has no len()
print("__main__.Proxy object" in str(p))
#: True
