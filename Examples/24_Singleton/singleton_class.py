# singleton_class.py
from typing import Any

class singleton:
    def __init__(self, klass: type) -> None:
        self.klass = klass
        self.instance: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"singleton.__call__({args}, {kwargs})")
        if self.instance is None:
            self.instance = self.klass(*args, **kwargs)
        return self.instance

@singleton
class Registry:
    def __init__(self, name: str, *, limit: int = 10) -> None:
        self.name = name
        self.limit = limit
        self.items: list[str] = []

first = Registry("primary", limit=3)
#: singleton.__call__(('primary',), {'limit': 3}
first.items.append("sausage")
second = Registry("ignored", limit=99)  # Arguments discarded
print(first is second, second.name, second.limit, second.items)
#: singleton.__call__(('ignored',), {'limit': 99}
#: True primary 3 ['sausage']
