# singleton_class.py
from typing import Any

class singleton:
    def __init__(self, wrapped: type) -> None:
        self.wrapped = wrapped
        self.instance: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"singleton.__call__({args}, {kwargs})")
        name = self.wrapped.__name__
        if self.instance is None:
            print(f"constructing {name}")
            self.instance = self.wrapped(*args, **kwargs)
        else:
            print(f"cached {name}: arguments discarded")
        return self.instance

@singleton
class Registry:
    def __init__(self, name: str, *,
                 limit: int = 10) -> None:
        print(f"Registry.__init__({name}, {limit})")
        self.name = name
        self.limit = limit
        self.items: list[str] = []
