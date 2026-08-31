# ask_tell.py
from dataclasses import dataclass, field
from typing import Protocol

class Ask(Protocol):
    def ask(self, prompt: str) -> str: ...

class Tell(Protocol):
    def tell(self, message: str) -> None: ...

def greet(ask: Ask, tell: Tell) -> None:
    name = ask.ask("What is your name? ")
    tell.tell(f"Hello, {name}!")

class Scripted:
    def ask(self, prompt: str) -> str:
        return "Alice"

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)

    def tell(self, message: str) -> None:
        self.messages.append(message)

captured = Capture()
greet(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
