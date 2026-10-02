# exercise_4.py
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

@dataclass(frozen=True)
class Webhook:
    url: str

type Notification = Email | Sms | Push | Webhook

def render(note: Notification, recipient: str) -> str:
    match note:
        case Email(subject):
            return f"Email to {recipient}: {subject}"
        case Sms(body):
            return f"SMS to {recipient}: {body}"
        case Push(title):
            return f"Push to {recipient}: {title}"
        case Webhook(url):
            return f"POST for {recipient} to {url}"
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
        case Webhook():
            return 0.0
        case _:
            assert_never(note)

hook = Webhook("https://example.com/hook")
print(render(hook, "Dana"))
#: POST for Dana to https://example.com/hook
print(cost(hook))
#: 0.0
