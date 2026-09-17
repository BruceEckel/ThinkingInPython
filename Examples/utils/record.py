# utils/record.py
from dataclasses import dataclass
from typing import dataclass_transform

@dataclass_transform(frozen_default=True)
def record[T](cls: type[T]) -> type[T]:
    return dataclass(frozen=True, slots=True)(cls)
