# broadcasting.py
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import dataclass_transform
from published import published

type Responder[T] = Callable[[T], None]

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls) -> None:
        built = dataclass(eq=False)(cls)  # [1]
        for field in fields(built):  # [2]
            prop = published(field.name)  # [3]
            setattr(cls, field.name, prop)  # [4]

    @property
    def _responders(self) -> list[Responder[T]]:
        return self.__dict__.setdefault("_responders", [])

    def respond(self, fn: Responder[T]) -> Responder[T]:
        self._responders.append(fn)
        return fn

    def disconnect(self, fn: Responder[T]) -> None:
        self._responders.remove(fn)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)
