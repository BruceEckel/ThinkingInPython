# event_bus.py
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

type Handler[E] = Callable[[E], None]

@dataclass(frozen=True)
class Deposit:
    amount: int

@dataclass(frozen=True)
class Withdraw:
    amount: int

@dataclass(frozen=True)
class Closed:
    reason: str

class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe[E](self, event_type: type[E],
                     handler: Handler[E]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: object) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)

def on_deposit(event: Deposit) -> None:
    print(f"+ deposit {event.amount}")

def audit(event: Deposit) -> None:
    print(f"  audit: a deposit of {event.amount}")

def on_withdraw(event: Withdraw) -> None:
    print(f"- withdraw {event.amount}")

bus = EventBus()
bus.subscribe(Deposit, on_deposit)
bus.subscribe(Deposit, audit)  # Two handlers for one event type
bus.subscribe(Withdraw, on_withdraw)

bus.publish(Deposit(100))
#: + deposit 100
#:   audit: a deposit of 100
bus.publish(Withdraw(30))
#: - withdraw 30
bus.publish(Closed("inactivity"))  # No handler: nothing happens
