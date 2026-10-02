# test_ch46_ask_and_greet.py
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from stateless import (Depend, Need, as_type, need,
                       run, supply)

@runtime_checkable
class Console(Protocol):
    def print(self, message: str) -> None: ...
    def read(self, prompt: str) -> str: ...

class Terminal:
    def print(self, message: str) -> None:
        print(message)

    def read(self, prompt: str) -> str:
        return input(prompt)

@dataclass
class Scripted:
    answer: str
    printed: list[str] = field(default_factory=list)

    def print(self, message: str) -> None:
        self.printed.append(message)

    def read(self, prompt: str) -> str:
        return self.answer

def ask_and_greet() -> Depend[Need[Console], None]:
    console = yield from need(Console)
    name = console.read("What is your name? ")
    console.print(f"Hello, {name}!")

def test_ask_and_greet_uses_the_answer_it_reads() -> None:
    scripted = Scripted("Alice")
    run(supply(as_type(Console)(scripted))(ask_and_greet)())
    assert scripted.printed == ["Hello, Alice!"]

scripted = Scripted("Bob")
run(supply(as_type(Console)(scripted))(ask_and_greet)())
print(scripted.printed)
#: ['Hello, Bob!']
