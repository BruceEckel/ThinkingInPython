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

notes: list[Notification] = [
    Email("Invoice ready"), Sms("Code: 5821"),
    Push("New message")]

for note in notes:
    print(render(note, "Dana"))
#: Email to Dana: Invoice ready
#: SMS to Dana: Code: 5821
#: Push to Dana: New message
print(round(sum(cost(n) for n in notes), 4))
#: 0.0215
