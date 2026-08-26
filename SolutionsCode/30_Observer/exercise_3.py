# exercise_3.py
from collections.abc import Callable

type Observer[T] = Callable[[T], None]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def subscribe(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def notify(self, data: T) -> None:
        failures: list[Exception] = []
        for observer in list(self._observers):
            try:
                observer(data)
            except Exception as e:
                failures.append(e)
        if failures:
            raise ExceptionGroup(
                "observer failures", failures)

received: list[int] = []

def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

obs = Observable[int]()
obs.subscribe(broken)
obs.subscribe(received.append)
try:
    obs.notify(7)
except* RuntimeError as group:
    print(len(group.exceptions), received)
#: 1 [7]
