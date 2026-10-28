# utils/meter.py
from dataclasses import dataclass

type Peak = int

@dataclass
class Meter:
    active: int = 0
    peak: Peak = 0

    def __enter__(self) -> None:
        self.active += 1
        self.peak = max(self.peak, self.active)

    def __exit__(self, exc_type: object, exc: object,
                 tb: object) -> None:
        self.active -= 1
