# exercise_4.py
import json
from dataclasses import dataclass

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

@dataclass(frozen=True)
class FullName:
    text: str

    def __post_init__(self) -> None:
        check(len(self.text.split()) >= 2,
              f"FullName({self.text!r})",
              "needs a first and last name")

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check("@" in self.text,
              f"EmailAddress({self.text!r})",
              "needs an @")

@dataclass(frozen=True)
class Person:
    name: FullName
    email: EmailAddress

def from_json(text: str) -> Person:
    data = json.loads(text)
    return Person(FullName(data["name"]),
                  EmailAddress(data["email"]))

bad_json = json.dumps(
    {"name": "Bruce Eckel", "email": "no-at-sign"})
try:
    from_json(bad_json)
except TypeFailure as e:
    print("from_json rejected:", e)
#: from_json rejected: EmailAddress('no-at-sign') needs an @
