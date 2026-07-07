# exercise_2.py
from dataclasses import dataclass

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check(self.text.count("@") == 1,
              f"EmailAddress({self.text!r})", "needs exactly one @")
        local, _, domain = self.text.partition("@")
        check(len(local) > 0 and len(domain) > 0,
              f"EmailAddress({self.text!r})",
              "needs text on both sides")

for bad in ["bruce", "b@@x.com", "@x.com", "b@", ""]:
    try:
        EmailAddress(bad)
    except TypeFailure as e:
        print("rejected:", bad, "->", e)
#: rejected: bruce -> EmailAddress('bruce') needs exactly one @
#: rejected: b@@x.com -> EmailAddress('b@@x.com') needs exactly one @
#: rejected: @x.com -> EmailAddress('@x.com') needs text on both sides
#: rejected: b@ -> EmailAddress('b@') needs text on both sides
#: rejected:  -> EmailAddress('') needs exactly one @

print(EmailAddress("bruce@example.com"))
#: EmailAddress(text='bruce@example.com')
