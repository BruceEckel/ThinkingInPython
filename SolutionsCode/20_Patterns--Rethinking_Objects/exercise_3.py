# exercise_3.py
from typing import NewType, Protocol

Price = NewType("Price", float)
Weight = NewType("Weight", float)

class Priced(Protocol):
    def total(self) -> Price: ...

class Package:
    def total(self) -> Weight:
        return Weight(2.5)

def charge(item: Priced) -> str:
    return f"${item.total():.2f}"

print(charge(Package()))  # type: ignore
#: $2.50
