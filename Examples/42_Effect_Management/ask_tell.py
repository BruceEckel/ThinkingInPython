# ask_tell.py
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

class Capture:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def tell(self, message: str) -> None:
        self.messages.append(message)

captured = Capture()
greet(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
