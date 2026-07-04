# protocols_typed.py
from dataclasses import dataclass
from typing import Protocol

class Displayable(Protocol):
    def display(self) -> str: ...

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

def show(t: Displayable) -> str:
    return t.display()

if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
#: Bicycle Bob
#: Glider 65
