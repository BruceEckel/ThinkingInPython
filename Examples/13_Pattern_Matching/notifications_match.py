# notifications_match.py
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Email:
    subject: str

@dataclass(frozen=True)
class Sms:
    body: str

@dataclass(frozen=True)
class Push:
    title: str

type Notification = Email | Sms | Push

def render(note: Notification, recipient: str) -> str:
    match note:
        case Email(subject):
            return f"Email to {recipient}: {subject}"
        case Sms(body):
            return f"SMS to {recipient}: {body}"
        case Push(title):
            return f"Push to {recipient}: {title}"
        case _:
            assert_never(note)

def cost(note: Notification) -> float:
    match note:
        case Email():
            return 0.001
        case Sms():
            return 0.02
        case Push():
            return 0.0005
        case _:
            assert_never(note)

email = Email("Invoice ready")
sms = Sms("Code: 5821")
push = Push("New message")

print(render(email, "Dana"))
#: Email to Dana: Invoice ready
print(render(sms, "Dana"))
#: SMS to Dana: Code: 5821
print(render(push, "Dana"))
#: Push to Dana: New message
print(round(cost(email) + cost(sms) + cost(push), 4))
#: 0.0215
