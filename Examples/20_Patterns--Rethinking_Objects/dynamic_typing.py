# dynamic_typing.py
from typing import Any
from exceptions import expect
from record import record

@record
class Bicycle:
    id: str

    def display(self) -> str:
        return f"Bicycle {self.id}"

@record
class Glider:
    size: int

    def display(self) -> str:
        return f"Glider {self.size}"

def show(t: Any) -> str:
    return t.display()

if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
    expect(AttributeError, show, 42)
#: Bicycle Bob
#: Glider 65
#: [AttributeError] 'int' object has no attribute 'display'
