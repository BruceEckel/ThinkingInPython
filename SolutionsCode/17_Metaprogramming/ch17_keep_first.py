# ch17_keep_first.py
from typing import Any

class KeepFirst(dict[str, Any]):
    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            return  # Discard the later definition
        super().__setitem__(key, value)

class First(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> KeepFirst:
        return KeepFirst()

class Handlers(metaclass=First):
    def on_open(self) -> None:
        print("first on_open")
    def on_open(self) -> None:  # noqa: F811
        print("second on_open")

Handlers().on_open()
#: first on_open
