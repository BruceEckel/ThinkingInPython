# singleton_decorator.py
# Singleton as a class decorator; simpler than a metaclass.
from collections.abc import Callable
from typing import Any
from display import display_object

def singleton(klass: type) -> Callable[..., Any]:
    instances: dict[type, Any] = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if klass not in instances:
            instances[klass] = klass(*args, **kwargs)
        return instances[klass]

    return get_instance

@singleton
class Registry:
    def __init__(self) -> None:
        self.items: list[str] = []

a = Registry()
b = Registry()
assert a is b
a.items.append("widget")
display_object(a)
#: === Registry ===
#: [Attributes]
#:   • items = ['widget']
#: [Methods]
#:   None
display_object(b)
#: === Registry ===
#: [Attributes]
#:   • items = ['widget']
#: [Methods]
#:   None
