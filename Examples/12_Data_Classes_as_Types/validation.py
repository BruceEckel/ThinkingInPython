# validation.py
from dataclasses import dataclass

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)
