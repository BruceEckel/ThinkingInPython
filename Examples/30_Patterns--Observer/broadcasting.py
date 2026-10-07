# broadcasting.py
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import dataclass_transform
from announcing import announcing

type Responder[T] = Callable[[T], None]

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls) -> None:
        built = dataclass(eq=False)(cls)
        for field in fields(built):
            setattr(cls, field.name, announcing(field.name))

    def responders(self) -> list[Responder[T]]:
        return self.__dict__.setdefault("_responders", [])

    def respond(self, fn: Responder[T]) -> Responder[T]:
        self.responders().append(fn)
        return fn

    def announce(self, data: T) -> None:
        for responder in list(self.responders()):
            responder(data)
