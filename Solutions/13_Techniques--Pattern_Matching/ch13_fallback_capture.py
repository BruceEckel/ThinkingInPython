# ch13_fallback_capture.py
from enum import Enum
from typing import Final

class Signal(Enum):
    STOP = "stop"
    GO = "go"
    CAUTION = "caution"

FALLBACK: Final[Signal] = Signal.CAUTION

class Defaults:
    FALLBACK: Final[Signal] = Signal.CAUTION

def act(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case FALLBACK:
            return f"fallback, FALLBACK is now {FALLBACK}"
    return "unreachable"

def dotted(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case Defaults.FALLBACK:
            return "fallback"
        case _:
            return "brake"

def guarded(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case other if other is FALLBACK:
            return "fallback"
        case _:
            return "brake"

print(act(Signal.STOP))
#: fallback, FALLBACK is now Signal.STOP
print(FALLBACK)
#: Signal.CAUTION
print(dotted(Signal.STOP), dotted(Signal.CAUTION))
#: brake fallback
print(guarded(Signal.STOP), guarded(Signal.CAUTION))
#: brake fallback
