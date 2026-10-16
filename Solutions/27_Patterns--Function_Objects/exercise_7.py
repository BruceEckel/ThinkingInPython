# exercise_7.py
import inspect
from dataclasses import dataclass
from typing import Final, dataclass_transform
from exceptions import expect

EVENTS: Final[set[type]] = set()

@dataclass_transform(frozen_default=True)
def event[E](cls: type[E]) -> type[E]:
    built = dataclass(frozen=True, slots=True)(cls)
    EVENTS.add(cls)  # The change: cls, not built
    return built

@dataclass_transform(frozen_default=True)
def handler[H](cls: type[H]) -> type[H]:
    call = vars(cls)["__call__"]
    sig = inspect.signature(call)
    handled = list(sig.parameters.values())[1].annotation
    if handled not in EVENTS:
        raise TypeError(f"{cls.__name__}: not an @event")
    return dataclass(frozen=True, slots=True)(cls)

@event
class Deposit:
    amount: int

print(len(EVENTS), Deposit in EVENTS)
#: 1 False
print(type(Deposit(5)) in EVENTS)
#: False

class Announce:
    prefix: str
    def __call__(self, event: Deposit) -> None:
        print(f"{self.prefix} deposit {event.amount}")

expect(TypeError, handler, Announce)
#: [TypeError] Announce: not an @event
