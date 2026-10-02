# exercise_3.py
from typing import NewType, Protocol
from record import record

Price = NewType("Price", float)
Weight = NewType("Weight", float)

class Priced(Protocol):
    def total(self) -> Price: ...

class Weighted(Protocol):
    def total(self) -> Weight: ...

@record
class Package:
    weight_kg: float

    def total(self) -> Weight:
        return Weight(self.weight_kg)

def charge(item: Priced) -> float:
    return item.total()

package = Package(4.5)
print(charge(package))  # type: ignore
#: 4.5
