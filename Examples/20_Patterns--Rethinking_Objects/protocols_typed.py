# protocols_typed.py
from typing import Protocol
from dynamic_typing import Bicycle, Glider

class Displayable(Protocol):
    def display(self) -> str: ...

def show(t: Displayable) -> str:
    return t.display()

if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
#: Bicycle Bob
#: Glider 65
