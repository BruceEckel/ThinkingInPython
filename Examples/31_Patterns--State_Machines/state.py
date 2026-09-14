# state.py
# A State has an operation, and can be moved
# into the next State given an Input:
from typing import Protocol

class State(Protocol):
    def run(self) -> None: ...
    def next(self, event: object) -> State: ...
