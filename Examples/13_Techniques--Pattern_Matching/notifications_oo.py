# notifications_oo.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

class Notification(ABC):
    @abstractmethod
    def render(self, recipient: str) -> str: ...

    @abstractmethod
    def cost(self) -> float: ...

@dataclass(frozen=True)
class Email(Notification):
    subject: str

    @override
    def render(self, recipient: str) -> str:
        return f"Email to {recipient}: {self.subject}"

    @override
    def cost(self) -> float:
        return 0.001

@dataclass(frozen=True)
class Sms(Notification):
    body: str

    @override
    def render(self, recipient: str) -> str:
        return f"SMS to {recipient}: {self.body}"

    @override
    def cost(self) -> float:
        return 0.02

@dataclass(frozen=True)
class Push(Notification):
    title: str

    @override
    def render(self, recipient: str) -> str:
        return f"Push to {recipient}: {self.title}"

    @override
    def cost(self) -> float:
        return 0.0005

notes: list[Notification] = [
    Email("Invoice ready"), Sms("Code: 5821"),
    Push("New message")]

for note in notes:
    print(note.render("Dana"))
#: Email to Dana: Invoice ready
#: SMS to Dana: Code: 5821
#: Push to Dana: New message
print(round(sum(n.cost() for n in notes), 4))
#: 0.0215
