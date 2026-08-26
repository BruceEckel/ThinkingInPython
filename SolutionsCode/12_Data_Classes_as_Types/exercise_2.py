# exercise_2.py
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

for bad in ["bruce", "b@@x.com", "@x.com", "b@", ""]:
    try:
        EmailAddress(bad)
    except TypeFailure as e:
        print("rejected:", e)
#: rejected: EmailAddress('bruce') needs exactly one @
#: rejected: EmailAddress('b@@x.com') needs exactly one @
#: rejected: EmailAddress('@x.com') needs text on both sides
#: rejected: EmailAddress('b@') needs text on both sides
#: rejected: EmailAddress('') needs exactly one @

print(EmailAddress("bruce@example.com"))
#: EmailAddress(text='bruce@example.com')
