# announcing.py
from typing import Any

def announcing(name: str) -> property:
    def read(self: Any) -> Any:
        return self.__dict__[name]

    def write(self: Any, value: Any) -> None:
        self.__dict__[name] = value
        self.announce(value)

    return property(read, write)
