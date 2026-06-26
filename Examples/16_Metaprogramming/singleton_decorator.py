# singleton_decorator.py
# Singleton as a class decorator; simpler than a metaclass.
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

def singleton(klass: type) -> Callable[..., Any]:
    instances: dict[type, Any] = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if klass not in instances:
            instances[klass] = klass(*args, **kwargs)
        return instances[klass]

    return get_instance

@singleton
@dataclass
class Registry:
    def __init__(self) -> None:
        self.items: list[str] = []

a = Registry()
b = Registry()
print(a)
## Registry()
print(b)
## Registry()
assert a is b
a.items.append("widget")
print(b.items)
## ['widget']
