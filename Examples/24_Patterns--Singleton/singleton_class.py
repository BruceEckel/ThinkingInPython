# singleton_class.py
from typing import Any

class singleton:
    def __init__(self, constructor: type) -> None:
        self.constructor = constructor
        self.instance: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"singleton.__call__({args}, {kwargs})")
        if self.instance is None:
            print(
                f"constructing {self.constructor.__name__}")
            self.instance = self.constructor(
                *args, **kwargs)
        else:
            print(
                f"using cached {self.constructor.__name__}")
            print(f"discarding {args}, {kwargs}")
        return self.instance

@singleton
class Registry:
    def __init__(self, name: str, *,
                 limit: int = 10) -> None:
        print(f"Registry.__init__({name}, {limit})")
        self.name = name
        self.limit = limit
        self.items: list[str] = []
