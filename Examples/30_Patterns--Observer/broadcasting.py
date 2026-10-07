# broadcasting.py
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import dataclass_transform
from announcing import announcing

type Responder[T] = Callable[[T], None]

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls) -> None:
        built = dataclass(eq=False)(cls)  # [1]
        for field in fields(built):  # [2]
            prop = announcing(field.name)  # [3]
            setattr(cls, field.name, prop)  # [4]

    @property
    def _responders(self) -> list[Responder[T]]:
        return self.__dict__.setdefault("_responders", [])

    def respond(self, fn: Responder[T]) -> Responder[T]:
        self._responders.append(fn)
        return fn

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)
