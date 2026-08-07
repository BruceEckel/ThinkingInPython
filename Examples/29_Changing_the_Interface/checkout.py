# checkout.py
from dataclasses import dataclass

@dataclass(frozen=True)
class _TaxRule:
    rate: float

@dataclass(frozen=True)
class _Discount:
    fraction: float

@dataclass(frozen=True)
class _PriceEngine:
    tax: _TaxRule
    cut: _Discount

    def compute(self, amount: float) -> float:
        net = amount * (1 - self.cut.fraction)
        return net * (1 + self.tax.rate)

def total(amount: float) -> float:
    engine = _PriceEngine(_TaxRule(0.08), _Discount(0.10))
    return engine.compute(amount)
