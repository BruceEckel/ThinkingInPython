# exercise_4.py
from typing import Self

class Tally:
    def __init__(self) -> None:
        self.count = 0

    def bump(self) -> Self:
        self.count += 1
        return self

class NamedTally(Tally):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def report(self) -> str:
        return f"{self.name}: {self.count}"

class LoudTally(NamedTally):
    def report(self) -> str:
        return super().report().upper()

t = LoudTally("clicks")
print(t.bump().bump().report())
#: CLICKS: 2
