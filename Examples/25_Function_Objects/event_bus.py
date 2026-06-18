# event_bus.py
# An event bus is a dict from each event type to the functions that
# care about it. Events are values; handlers are plain functions.
# Publishing an event calls every handler for that event's type.
# No Handler base class, and no registration ceremony.
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


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
        self._handlers: dict[type, list[Callable[[Any], None]]] = {}

    def subscribe[E](self, event_type: type[E],
                     handler: Callable[[E], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

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
bus.subscribe(Deposit, audit)        # two handlers for one event type
bus.subscribe(Withdraw, on_withdraw)

bus.publish(Deposit(100))
bus.publish(Withdraw(30))
bus.publish(Closed("inactivity"))    # no handler: nothing happens
