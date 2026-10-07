# event_bus.py
from collections import defaultdict
from collections.abc import Callable
from typing import Any
from record import record

type Handler[E] = Callable[[E], None]

@record
class Deposit:
    amount: int

@record
class Withdraw:
    amount: int

@record
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
