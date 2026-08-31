# messenger.py
from dataclasses import dataclass

@dataclass
class Messenger:
    name: str
    number: int
    depth: float = 0.0  # Default value
