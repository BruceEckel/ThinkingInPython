# watched.py
from collections.abc import Callable

type Watcher = Callable[[str, object], None]

class Watched:
    _watchers: list[Watcher]  # Bare annotation

    def __init__(
        self, celsius: float, humidity: float
    ) -> None:
        # __setattr__() reads _watchers, so it
        # must exist before the first assignment
        self.__dict__["_watchers"] = []
        self.celsius = celsius
        self.humidity = humidity

    def watch(self, watcher: Watcher) -> None:
        self._watchers.append(watcher)

    def __setattr__(
        self, name: str, value: object
    ) -> None:
        super().__setattr__(name, value)
        for watcher in list(self._watchers):
            watcher(name, value)

w = Watched(20.0, 0.4)
changes: list[tuple[str, object]] = []
w.watch(lambda n, v: changes.append((n, v)))
w.celsius = 25.0
w.humidity = 0.5
print(changes)
#: [('celsius', 25.0), ('humidity', 0.5)]
