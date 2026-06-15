# duck_typing.py
# Duck typing: any type works as long as it has the method that gets
# called. There is no base class and no type union. The check happens
# only at run time, when the method is called.
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Bicycle:
    id: str

    def display(self) -> str:
        return f"Bicycle {self.id}"


@dataclass(frozen=True)
class Glider:
    size: int

    def display(self) -> str:
        return f"Glider {self.size}"


def show(t: Any) -> str:
    return t.display()


if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
