# prepare_namespace.py
from typing import Any
from exceptions import ignore

class NoDuplicates(dict[str, Any]):
    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            raise TypeError(f"{key} defined twice")
        super().__setitem__(key, value)

class Strict(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> NoDuplicates:
        return NoDuplicates()

with ignore(TypeError):
    class Handlers(metaclass=Strict):
        def on_open(self) -> None: ...
        def on_close(self) -> None: ...
        def on_open(self) -> None: ...  # noqa: F811
#: TypeError('on_open defined twice')
