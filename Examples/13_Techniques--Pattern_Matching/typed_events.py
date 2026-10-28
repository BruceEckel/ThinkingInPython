# typed_events.py
from typing import Literal, TypedDict

class Click(TypedDict):
    type: Literal["click"]
    x: int
    y: int

class Key(TypedDict):
    type: Literal["key"]
    key: str

type Event = Click | Key

def handle(event: Event) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y}), sum {x + y}"
        case {"type": "key", "key": key}:
            return f"Key {key.upper()}"
        case _:
            return "Unrecognized event"

print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20), sum 30
print(handle({"type": "key", "key": "Enter"}))
#: Key ENTER
