# exercise_5.py
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

type Handler[E] = Callable[[E], None]

@dataclass(frozen=True)
class Deposit:
    amount: int

@dataclass(frozen=True)
class BigDeposit(Deposit):
    pass

class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe[E](self, event_type: type[E],
                     handler: Handler[E]) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe[E](self, event_type: type[E],
                       handler: Handler[E]) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: object) -> None:
        for cls in type(event).__mro__:  # Parents last
            for handler in self._handlers.get(cls, []):
                handler(event)

def on_deposit(event: Deposit) -> None:
    print(f"deposit {event.amount}")

def on_big(event: BigDeposit) -> None:
    print(f"big deposit {event.amount}")

bus = EventBus()
bus.subscribe(Deposit, on_deposit)
bus.subscribe(BigDeposit, on_big)

bus.publish(BigDeposit(500))
#: big deposit 500
#: deposit 500
bus.publish(Deposit(10))
#: deposit 10

bus.unsubscribe(Deposit, on_deposit)
bus.publish(BigDeposit(500))
#: big deposit 500
