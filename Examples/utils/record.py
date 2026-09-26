# utils/record.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import dataclass_transform, overload

@overload
def record[T](cls: type[T], /) -> type[T]: ...
@overload
def record[T](
    *, slots: bool = True
) -> Callable[[type[T]], type[T]]: ...
@dataclass_transform(frozen_default=True)
def record[T](
    cls: type[T] | None = None, /, *, slots: bool = True
) -> type[T] | Callable[[type[T]], type[T]]:
    def apply(c: type[T]) -> type[T]:
        return dataclass(frozen=True, slots=slots)(c)
    return apply if cls is None else apply(cls)
