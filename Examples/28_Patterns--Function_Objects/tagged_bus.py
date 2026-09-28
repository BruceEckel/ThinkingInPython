# tagged_bus.py
import inspect
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Final, Protocol, dataclass_transform

EVENTS: Final[set[type]] = set()
HANDLES: Final[dict[type, type]] = {}

@dataclass_transform(frozen_default=True)
def event[E](cls: type[E]) -> type[E]:
    built = dataclass(frozen=True, slots=True)(cls)
    EVENTS.add(built)
    return built

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
    built = dataclass(frozen=True, slots=True)(cls)
    HANDLES[built] = handled
    return built

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
