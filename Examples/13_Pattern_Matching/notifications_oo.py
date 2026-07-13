# notifications_oo.py
from abc import ABC, abstractmethod
from typing import override

class Notification(ABC):
    @abstractmethod
    def render(self, recipient: str) -> str: ...

    @abstractmethod
    def cost(self) -> float: ...

class Email(Notification):
    def __init__(self, subject: str) -> None:
        self.subject = subject

    @override
    def render(self, recipient: str) -> str:
        return f"Email to {recipient}: {self.subject}"

    @override
    def cost(self) -> float:
        return 0.001

class Sms(Notification):
    def __init__(self, body: str) -> None:
        self.body = body

    @override
    def render(self, recipient: str) -> str:
        return f"SMS to {recipient}: {self.body}"

    @override
    def cost(self) -> float:
        return 0.02

class Push(Notification):
    def __init__(self, title: str) -> None:
        self.title = title

    @override
    def render(self, recipient: str) -> str:
        return f"Push to {recipient}: {self.title}"

    @override
    def cost(self) -> float:
        return 0.0005

email = Email("Invoice ready")
sms = Sms("Code: 5821")
push = Push("New message")

print(email.render("Dana"))
#: Email to Dana: Invoice ready
print(sms.render("Dana"))
#: SMS to Dana: Code: 5821
print(push.render("Dana"))
#: Push to Dana: New message
print(round(email.cost() + sms.cost() + push.cost(), 4))
#: 0.0215
