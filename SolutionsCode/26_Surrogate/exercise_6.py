# exercise_6.py
from typing import Any

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

class Proxy:
    def __init__(self) -> None:
        self.__implementation = Words()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

    def __len__(self) -> int:
        return len(self.__implementation)

p = Proxy()
print(len(p))
#: 2
