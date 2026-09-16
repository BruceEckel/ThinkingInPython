# tagged_bus.py
import inspect
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Final, Protocol, dataclass_transform
from exceptions import expect

EVENTS: Final[set[type]] = set()
HANDLES: Final[dict[type, type]] = {}

@dataclass_transform(frozen_default=True)
def event[E](cls: type[E]) -> type[E]:
    EVENTS.add(cls)
    return dataclass(frozen=True)(cls)

class Handler[E](Protocol):
    def __call__(self, event: E, /) -> None: ...

@dataclass_transform(frozen_default=True)
def handler[H](cls: type[H]) -> type[H]:
    call = vars(cls).get("__call__")
    if call is None:
        raise TypeError(f"{cls.__name__} has no __call__")
    sig = inspect.signature(call)
    handled = list(sig.parameters.values())[1].annotation
    if handled not in EVENTS:
        raise TypeError(f"{cls.__name__}: not an @event")
    HANDLES[cls] = handled
    return dataclass(frozen=True)(cls)

class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe(self, handler: Handler[Any]) -> None:
        handled = HANDLES.get(type(handler))
        if handled is None:
            name = type(handler).__name__
            raise TypeError(f"{name} is not a @handler")
        self._handlers[handled].append(handler)

    def publish(self, event: object) -> None:
        if type(event) not in EVENTS:
            name = type(event).__name__
            raise TypeError(f"{name} is not an @event")
        for handler in self._handlers.get(type(event), []):
            handler(event)

@event
class Deposit:
    amount: int

@event
class Withdraw:
    amount: int

@event
class Closed:
    reason: str

@handler
class Announce:
    prefix: str
    def __call__(self, event: Deposit) -> None:
        print(f"{self.prefix} deposit {event.amount}")

@handler
class Audit:
    threshold: int
    def __call__(self, event: Deposit) -> None:
        if event.amount > self.threshold:
            print(f"  audit: large deposit {event.amount}")

@handler
class OnWithdraw:
    def __call__(self, event: Withdraw) -> None:
        print(f"- withdraw {event.amount}")

bus = EventBus()
bus.subscribe(Announce("+"))
bus.subscribe(Audit(threshold=50))
bus.subscribe(OnWithdraw())
bus.publish(Deposit(100))
#: + deposit 100
#:   audit: large deposit 100
bus.publish(Deposit(10))
#: + deposit 10
bus.publish(Withdraw(30))
#: - withdraw 30
bus.publish(Closed("inactivity"))  # An event, no handler
expect(TypeError, bus.publish, "Deposit")
#: [TypeError] str is not an @event
