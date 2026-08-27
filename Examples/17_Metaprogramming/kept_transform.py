# kept_transform.py
from dataclasses import dataclass
from typing import dataclass_transform

@dataclass_transform(frozen_default=True)
def model[T](cls: type[T]) -> type[T]:
    return dataclass(frozen=True)(cls)

@model
class User:
    name: str
    age: int = 0

u = User("Bruce", 30)
print(u)
#: User(name='Bruce', age=30)
# ty: Property `age` defined in `User` is read-only:
# u.age = 9
