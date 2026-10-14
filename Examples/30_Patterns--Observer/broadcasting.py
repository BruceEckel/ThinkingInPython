# broadcasting.py
from dataclasses import dataclass, fields
from typing import dataclass_transform
from broadcaster import Responder
from published import published

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        built = dataclass(eq=False)(cls)  # [1]
        for field in fields(built):  # [2]
            prop = published(field.name)  # [3]
            setattr(cls, field.name, prop)  # [4]

    @property
    def _responders(self) -> list[Responder[T]]:
        return self.__dict__.setdefault("_responders", [])

    def respond(
        self, responder: Responder[T]
    ) -> Responder[T]:
        self._responders.append(responder)
        return responder

    def disconnect(self, responder: Responder[T]) -> None:
        self._responders.remove(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)
