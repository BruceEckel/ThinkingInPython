# exercise_11.py
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from stateless import (Depend, Need, as_type, need,
                       run, supply)

@runtime_checkable
class Screen(Protocol):
    def print(self, message: str) -> None: ...

@runtime_checkable
class Recorder(Protocol):
    def record(self, message: str) -> None: ...

@dataclass
class Terminal:
    def print(self, message: str) -> None:
        print(message)

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)
    def record(self, message: str) -> None:
        self.messages.append(message)

def to_screen(name: str) -> Depend[Need[Screen], None]:
    device = yield from need(Screen)
    device.print(f"Hello, {name}!")

def to_log(name: str) -> Depend[Need[Recorder], None]:
    device = yield from need(Recorder)
    device.record(f"Hello, {name}!")

capture = Capture()
run(supply(as_type(Screen)(Terminal()))(to_screen)("Alice"))
#: Hello, Alice!
run(supply(as_type(Recorder)(capture))(to_log)("Bob"))
print(capture.messages)
#: ['Hello, Bob!']
