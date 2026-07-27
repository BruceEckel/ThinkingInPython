# recorder.py
from typing import override
from greeter import Console

class Recorder(Console):
    def __init__(self) -> None:
        self.messages: list[str] = []
    @override
    def print(self, message: str) -> None:
        self.messages.append(message)
