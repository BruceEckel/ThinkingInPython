# multi_protocol.py
import json
from dataclasses import asdict, dataclass
from typing import Protocol

class Priced(Protocol):
    def total(self) -> float: ...

class Serializable(Protocol):
    def to_json(self) -> str: ...

class Loggable(Protocol):
    def describe(self) -> str: ...

@dataclass(frozen=True)
class Invoice:
    amount: float
    customer: str

    def total(self) -> float:
        return self.amount

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    def describe(self) -> str:
        return f"Invoice for {self.customer}"

def charge(item: Priced) -> float:
    return item.total()

def persist(item: Serializable) -> str:
    return item.to_json()

def audit(item: Loggable) -> str:
    return item.describe()

if __name__ == "__main__":
    invoice = Invoice(19.99, "Ada")
    print(charge(invoice))
    print(persist(invoice))
    print(audit(invoice))
#: 19.99
#: {"amount": 19.99, "customer": "Ada"}
#: Invoice for Ada
