# post_init_normalize.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(frozen=True)
class Email:
    text: str

    def __post_init__(self) -> None:
        self.text = self.text.lower()  # type: ignore

expect(Exception, Email, "Grace@Example.com")
#: [FrozenInstanceError] cannot assign to field 'text'

@dataclass(frozen=True)
class Normalized:
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", self.text.lower())

print(Normalized("Grace@Example.com"))
#: Normalized(text='grace@example.com')
