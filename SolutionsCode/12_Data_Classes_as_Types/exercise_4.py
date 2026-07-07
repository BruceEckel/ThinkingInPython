# exercise_4.py
import json
from dataclasses import dataclass

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

@dataclass(frozen=True)
class FullName:
    text: str

    def __post_init__(self) -> None:
        check(len(self.text.split()) >= 2, f"FullName({self.text!r})",
              "needs a first and last name")

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check("@" in self.text, f"EmailAddress({self.text!r})",
              "needs an @")

@dataclass(frozen=True)
class Person:
    name: FullName
    email: EmailAddress

def from_json(text: str) -> Person:
    data = json.loads(text)
    return Person(FullName(data["name"]), EmailAddress(data["email"]))

bad_json = json.dumps({"name": "Bruce Eckel", "email": "no-at-sign"})
try:
    from_json(bad_json)
except TypeFailure as e:
    print("from_json rejected bad email:", e)
#: from_json rejected bad email: EmailAddress('no-at-sign') needs an @
