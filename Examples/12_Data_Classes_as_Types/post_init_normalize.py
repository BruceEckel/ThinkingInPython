# post_init_normalize.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    text: str

    def __post_init__(self) -> None:
        self.text = self.text.lower()  # type: ignore

try:
    Email("Bruce@Example.com")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: FrozenInstanceError: cannot assign to field 'text'

@dataclass(frozen=True)
class Normalized:
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", self.text.lower())

print(Normalized("Bruce@Example.com"))
#: Normalized(text='bruce@example.com')
