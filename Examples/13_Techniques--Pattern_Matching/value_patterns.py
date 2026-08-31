# value_patterns.py
from enum import Enum
from typing import Final

class Signal(Enum):
    STOP = "stop"
    GO = "go"

DEFAULT: Final[Signal] = Signal.STOP

def act(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case Signal.STOP:
            return "brake"

def broken(s: Signal) -> str:
    match s:
        case DEFAULT:
            return f"DEFAULT is now {DEFAULT}"
    return "unreachable"

print(act(Signal.GO), act(Signal.STOP))
#: accelerate brake
print(broken(Signal.GO))
#: DEFAULT is now Signal.GO
print(DEFAULT)
#: Signal.STOP
