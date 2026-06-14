# SingletonDecorator.py
# The same idea as a class decorator. Simpler than a metaclass.
from typing import Any, Callable


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
print(b.items)

""" Output:
['widget']
"""
