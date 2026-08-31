# exercise_4.py
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Email:
    subject: str

@dataclass(frozen=True)
class Webhook:
    url: str

type Notification = Email | Webhook

def render(note: Notification, recipient: str) -> str:
    match note:
        case Email(subject):
            return f"Email to {recipient}: {subject}"
        case Webhook(url):
            return f"POST for {recipient} to {url}"
        case _:
            assert_never(note)

print(render(Webhook("https://example.com/hook"), "Dana"))
#: POST for Dana to https://example.com/hook
