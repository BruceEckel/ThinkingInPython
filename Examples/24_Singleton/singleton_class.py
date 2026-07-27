# singleton_class.py
from typing import Any

class singleton:
    def __init__(self, constructor: type) -> None:
        self.constructor = constructor
        self.instance: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"singleton.__call__({args}, {kwargs})")
        if self.instance is None:
            print(f"constructing {self.constructor.__name__}")
            self.instance = self.constructor(*args, **kwargs)
        else:
            print(f"using cached {self.constructor.__name__}")
            print(f"discarding {args}, {kwargs}")
        return self.instance

@singleton
class Registry:
    def __init__(self, name: str, *, limit: int = 10) -> None:
        print(f"Registry.__init__({name}, {limit})")
        self.name = name
        self.limit = limit
        self.items: list[str] = []

first = Registry("primary", limit=3)
#: singleton.__call__(('primary',), {'limit': 3})
#: constructing Registry
#: Registry.__init__(primary, 3)
first.items.append("spam")
first.items.append("eggs")
second = Registry("secondary", limit=99)
#: singleton.__call__(('secondary',), {'limit': 99})
#: using cached Registry
#: discarding ('secondary',), {'limit': 99}
print(first is second, second.name, second.limit, second.items)
#: True primary 3 ['spam', 'eggs']
