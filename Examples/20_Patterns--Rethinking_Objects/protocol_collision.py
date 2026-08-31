# protocol_collision.py
from dataclasses import dataclass
from typing import Protocol

class Priced(Protocol):
    def total(self) -> float: ...

class Weighted(Protocol):
    def total(self) -> float: ...

@dataclass(frozen=True)
class Package:
    weight_kg: float

    def total(self) -> float:
        return self.weight_kg  # Weight, not a price

def charge(item: Priced) -> float:
    return item.total()

if __name__ == "__main__":
    package = Package(4.5)
    print(charge(package))  # Silently treated as a price
#: 4.5
