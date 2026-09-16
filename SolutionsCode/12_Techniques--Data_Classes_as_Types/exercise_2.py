# exercise_2.py
from dataclasses import dataclass
from exceptions import expect

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
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check(self.text.count("@") == 1,
              f"EmailAddress({self.text!r})",
              "needs exactly one @")
        local, _, domain = self.text.partition("@")
        check(len(local) > 0 and len(domain) > 0,
              f"EmailAddress({self.text!r})",
              "needs text on both sides")

for bad in ["grace", "b@@x.com", "@x.com", "b@", ""]:
    expect(TypeFailure, EmailAddress, bad)
#: [TypeFailure] EmailAddress('grace') needs exactly one @
#: [TypeFailure] EmailAddress('b@@x.com') needs exactly one
#: @
#: [TypeFailure] EmailAddress('@x.com') needs text on both
#: sides
#: [TypeFailure] EmailAddress('b@') needs text on both sides
#: [TypeFailure] EmailAddress('') needs exactly one @

print(EmailAddress("grace@example.com"))
#: EmailAddress(text='grace@example.com')
