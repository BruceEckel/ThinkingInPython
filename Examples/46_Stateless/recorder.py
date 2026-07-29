# recorder.py
from dataclasses import dataclass, field
from typing import override
from greeter import Console

@dataclass
class Recorder(Console):
    messages: list[str] = field(default_factory=list)
    @override
    def print(self, message: str) -> None:
        self.messages.append(message)
